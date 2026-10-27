// category: mixed  (real program 043)
// Codeforces submission 18536921, problem 622/A, GNU C, 2016-06-17
// https://codeforces.com/contest/622/submission/18536921
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

    long long int i = 1 , n ;



    scanf("%I64d",&n) ;



    while(n)

    {

        n = n - i ;

        if(n <= 0){

            printf("%I64d",n+i);

            exit(0);

        }

        i++;

    }

    return 0 ;

}
