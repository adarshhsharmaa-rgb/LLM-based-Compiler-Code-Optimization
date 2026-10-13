// category: repeated_expr  (real program 022)
// Codeforces submission 22084168, problem 670/A, C++14 (GCC 6-32), 2016-11-06
// https://codeforces.com/contest/670/submission/22084168
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <cstdio>

#include <iostream>



using namespace std;

int main()

{

     int a,b,n,c,max,min;



    scanf("%d",&n);

    min=n/7;

    min*=2;



    if((n%7)>=2)

        max=min+2;

    if(n%7==1 || n%7==0)



    max=min+(n%7);

    if(n%7==6)

        min+=1;

    printf("%d %d",min,max);

    return 0;

}
