// category: arithmetic  (real program 056)
// Codeforces submission 39616426, problem 996/A, C++17 (GCC 7-32), 2018-06-24
// https://codeforces.com/contest/996/submission/39616426
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    long int n;
    int count=0, d;
    scanf("%ld", &n);
    d = n/100;
    count+=d;
    n = n % 100;
    d = n/20;
    count+=d;
    n = n%20;
    d = n/10;
    count+=d;
    n= n%10;
    d= n/5;
    count+=d;
    n = n%5;
    count+=n;
    printf("%d\n", count);
    return 0;
}
