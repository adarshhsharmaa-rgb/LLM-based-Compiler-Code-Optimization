// category: nested  (real program 028)
// Codeforces submission 21918228, problem 268/B, GNU C, 2016-10-31
// https://codeforces.com/contest/268/submission/21918228
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>



int main()



{

    long long n, c;



    scanf("%lld", &n);



    c = n * (n - 1) * (n + 1) / 6 + n;



    printf("%lld\n", c);



    return 0;

}
