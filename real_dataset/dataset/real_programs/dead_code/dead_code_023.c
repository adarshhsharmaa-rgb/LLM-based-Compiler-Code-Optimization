// category: dead_code  (real program 023)
// Codeforces submission 35684466, problem 935/A, GNU C11, 2018-02-25
// https://codeforces.com/contest/935/submission/35684466
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>
#include <stdlib.h>

int main()
{
    int i,j,k,l,m=0,n=0;

    scanf("%d",&k);

    for(i=1;i<=k/2;i++){

        if(k%i==0){

            n=n+1;
        }
    }


    printf("%d",n);
    return 0;
}
