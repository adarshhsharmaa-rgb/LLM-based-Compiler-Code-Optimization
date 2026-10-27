// category: conditionals  (real program 073)
// Codeforces submission 29895937, problem 842/A, GNU C++, 2017-08-29
// https://codeforces.com/contest/842/submission/29895937
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
long long l,r,x,y,k,l1,r1;
int main(){
    scanf("%I64d%I64d%I64d%I64d%I64d",&l,&r,&x,&y,&k);
    l1=l/k+(l%k>0);
    r1=r/k;
    if (l1>r1||x>r1||y<l1) printf("NO\n");
    else printf("YES\n"); 
}
