#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>
#include <getopt.h>

#ifndef OFFSET
#define OFFSET 2208988800ULL
#endif


void ntp2tv(uint64_t *ntp, struct timeval *tv);

void tv2ntp(struct timeval *tv, uint64_t *ntp);

size_t print_tv(struct timeval *t);

size_t print_ntp(uint64_t *ntp);
