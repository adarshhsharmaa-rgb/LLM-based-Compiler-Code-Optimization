// category: conditionals  (real program 004)
// Codeforces submission 21961318, problem 486/A, GNU C, 2016-11-01
// https://codeforces.com/contest/486/submission/21961318
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

    long long int n,s;

    scanf("%I64d",&n);

    if(n%2==0){

        s=n/2;

        printf("%I64d\n",s);

    }

    else{

        s=(n+1)/2;

        printf("-%I64d\n",s);

    }

    return 0;

}
