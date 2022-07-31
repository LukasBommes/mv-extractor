# include "time_cvt.hpp"


void ntp2tv(uint64_t *ntp, struct timeval *tv)
{
    uint64_t aux = 0;
    uint8_t *p = (uint8_t *)ntp + 8;
    int i;

    /* we get the ntp in network byte order, so we must
     * convert it to host byte order. */
    for (i = 0; i < 4; i++) {
        aux <<= 8;
        aux |= *--p;
    }

    /* now we have in aux the NTP seconds offset */
    aux -= OFFSET;
    tv->tv_sec = aux;

    /* let's go with the fraction of second */
    aux = 0;
    for (; i < 8; i++) {
        aux <<= 8;
        aux |= *--p;
    }

    /* now we have in aux the NTP fraction (0..2^32-1) */
    aux *= 1000000; /* multiply by 1e6 */
    aux >>= 32;     /* and divide by 2^32 */
    tv->tv_usec = aux;
}


void tv2ntp(struct timeval *tv, uint64_t *ntp)
{
    uint64_t aux = 0;
    uint8_t *p = (uint8_t *)ntp;
    int i;

    aux = tv->tv_usec;
    aux <<= 32;
    aux /= 1000000;

    /* we set the ntp in network byte order */
    for (i = 0; i < 4; i++) {
        *p++ = aux & 0xff;
        aux >>= 8;
    }

    aux = tv->tv_sec;
    aux += OFFSET;

    /* let's go with the fraction of second */
    for (; i < 8; i++) {
        *p++ = aux & 0xff;
        aux >>= 8;
    }

}


size_t print_tv(struct timeval *t)
{
    return printf("%ld.%06ld\n", t->tv_sec, t->tv_usec);
}


size_t print_ntp(uint64_t *ntp)
{
    uint8_t *p = (uint8_t *)ntp;
    int i;
    int res = 0;
    for (i = 0; i < 8; i++) {
        if (i == 4)
            res += printf(".");
        res += printf("%02x", p[7-i]);
    }
    res += printf("\n");
    return res;
}
