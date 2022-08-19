// gcc src/time_cvt.cpp src/time_cvt_test.cpp
#include "time_cvt.hpp"


int main(int argc, char *argv[])
{
    struct timeval t;
    uint64_t ntp = 16197291649570726477;

    printf("ntp: "); print_ntp(&ntp);

    printf("ntp2tv\n");
    ntp2tv(&ntp, &t);
    printf("tv : "); print_tv(&t);
    printf("ntp: "); print_ntp(&ntp);

    printf("tv2ntp\n");
    tv2ntp(&t, &ntp);
    printf("tv : "); print_tv(&t);
    printf("ntp: "); print_ntp(&ntp);
}
