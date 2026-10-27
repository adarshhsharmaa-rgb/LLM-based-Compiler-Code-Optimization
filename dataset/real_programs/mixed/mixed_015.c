// category: mixed  (real program 015)
// Codeforces submission 564616, problem 73/A, GNU C++, 2011-07-25
// https://codeforces.com/contest/73/submission/564616
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
#include<algorithm>
#include<iostream>
using namespace std;

int main(void)
{
    long long x,y,z,k;
    scanf("%I64d%I64d%I64d%I64d", &x,&y,&z,&k);
    while ( x+y+z-3>k){
          if ( x > y && x > z) x--;
          else if (y > z) y--;
          else z--;
    }
    printf("%I64d", x*y*z);
}
