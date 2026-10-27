// category: mixed  (real program 005)
// Codeforces submission 18605826, problem 678/C, GNU C, 2016-06-19
// https://codeforces.com/contest/678/submission/18605826
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>



int main()

{

    long long int n, a, b, p, q, red, blue, mixed, lcm, t, y, gcd;

    scanf("%I64d%I64d%I64d%I64d%I64d",&n,&a,&b,&p,&q);

    red = n/a;

    blue = n/b;

    y = a*b;

    while (b != 0) {

        t = b;

        b = a % b;

        a = t;

    }

    gcd = a;

    lcm = y/gcd;

    mixed = n/lcm;



    if(p > q){

        printf("%I64d",((red*p)+(blue-mixed)*q));

    }

    else {

        printf("%I64d",((blue*q)+(red-mixed)*p));

    }

    return 0;



}
