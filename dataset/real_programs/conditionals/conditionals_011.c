// category: conditionals  (real program 011)
// Codeforces submission 20301320, problem 638/A, C++14 (GCC 6-32), 2016-08-31
// https://codeforces.com/contest/638/submission/20301320
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;

int n,a;



int main()

{

    scanf("%d%d",&n,&a);

    if (a%2==0)

    {

        printf("%d",(n-a)/2 +1);

    }

    else

        printf("%d",(a-1)/2 +1);

}
