/* SPDX-License-Identifier: GPL-3.0-or-later */
/* Headless native equivalent of tests/e2e/variant-date-probe.cs. */
#include <windows.h>
#include <oleauto.h>
#include <stdio.h>
#include <math.h>
int main(void)
{
    double values[] = {2958465.9999999884,2958465.0,2958465.999994,2958465.999995,46387.99999537037,0.0,-657434.0};
    unsigned int i, failures=0;
    for (i=0;i<sizeof(values)/sizeof(values[0]);i++)
    {
        SYSTEMTIME st={0};
        double back=NAN;
        int converted=VariantTimeToSystemTime(values[i],&st);
        int restored=converted?SystemTimeToVariantTime(&st,&back):0;
        int ok=converted && restored && st.wYear<=9999;
        failures+=!ok;
        printf("%.17g %04u-%02u-%02u %02u:%02u:%02u to=%d back=%d %.17g %s\n",values[i],st.wYear,st.wMonth,st.wDay,st.wHour,st.wMinute,st.wSecond,converted,restored,back,ok?"ok":"FAIL");
    }
    {
        SYSTEMTIME st;
        int rejected=!VariantTimeToSystemTime(2958466.0,&st);
        failures+=!rejected;
        printf("year 10000 rejected=%d\n",rejected);
    }
    printf("RESULT passed=%u failed=%u\n",8-failures,failures);
    return failures?1:0;
}
