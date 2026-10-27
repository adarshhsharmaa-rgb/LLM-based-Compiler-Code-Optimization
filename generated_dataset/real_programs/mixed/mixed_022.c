// category: mixed  (real program 022)
// Codeforces submission 18097783, problem 669/A, GNU C, 2016-05-26
// https://codeforces.com/contest/669/submission/18097783
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>

int main()

{

    long int n , count  = 0,  sum = 0 , i = 0  ;

    scanf("%ld",&n);

    while(sum < n)

    {

        if(!(i%2))

        {

            sum += 1 ;

            count++ ;

        }

        else

        {

            sum += 2 ;

            count++;

        }

        i++;

    }



    if(sum>n)count -= 1 ;

    printf("%ld",count);

    return 0 ;

}
