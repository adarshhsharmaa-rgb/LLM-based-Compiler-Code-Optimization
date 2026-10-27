// category: loops  (real program 024)
// Codeforces submission 13316812, problem 552/B, GNU C++, 2015-09-30
// https://codeforces.com/contest/552/submission/13316812
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
long long i,a,cvp;
int main(){
    scanf("%lld",&a);
    for(i=1;i<=a;i*=10)
        cvp+=a-i+1;
    printf("%lld\n",cvp);
}
