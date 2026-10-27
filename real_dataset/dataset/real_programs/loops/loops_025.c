// category: loops  (real program 025)
// Codeforces submission 41348372, problem 1017/C, C++14 (GCC 6-32), 2018-08-08
// https://codeforces.com/contest/1017/submission/41348372
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int n;
int main(){
    scanf("%d",&n);
    int rt=1;
    for(; rt*rt<n; rt++);
    int rp = n/rt;
    for(int i=1; i<=rp; i++){
        for(int j=i*rt; j>(i-1)*rt; j--) printf("%d ",j);
    }
    for(int i=n; i>rp*rt; i--) printf("%d ",i);
    return 0;
}
