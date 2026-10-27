// category: conditionals  (real program 064)
// Codeforces submission 38224316, problem 979/A, C++17 (GCC 7-32), 2018-05-14
// https://codeforces.com/contest/979/submission/38224316
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
//hi
#include<bits/stdc++.h>
using namespace std;
#define PB push_back
#define MP make_pair
#define F first
#define S second
typedef long long int LL;
int main(void){
    LL n;
    scanf("%lld",&n);
    n++;
    if(n==1) printf("0\n");
    else if(n%2==0) printf("%lld\n",n/2);
    else printf("%lld\n",n);
    return 0;
}
