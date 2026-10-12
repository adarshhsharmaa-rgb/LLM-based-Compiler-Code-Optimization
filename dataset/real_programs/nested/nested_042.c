// category: nested  (real program 042)
// Codeforces submission 44627739, problem 1031/A, GNU C++11, 2018-10-21
// https://codeforces.com/contest/1031/submission/44627739
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <iostream>
#include<algorithm>
using namespace std;
int main()
{
    int w,h,k;
    scanf("%d%d%d",&w,&h,&k);
    printf("%d",2*k*w+2*h*k-4*k-8*(k)*(k-1));
    return 0;
}
