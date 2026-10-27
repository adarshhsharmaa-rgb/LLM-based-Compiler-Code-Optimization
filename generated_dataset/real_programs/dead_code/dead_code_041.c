// category: dead_code  (real program 041)
// Codeforces submission 36364415, problem 926/A, GNU C, 2018-03-17
// https://codeforces.com/contest/926/submission/36364415
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <stdio.h>

#define ll long long

int main(){

    ll x,y, p=1, q, i, j, ans=0;
    scanf("%lld %lld", &x, &y);

    for(i=1; p<=y; i++){

        q=p;

        for(j=1; q<=y; q*=2){

            if(q>=x && q<=y)ans++;

        }
        p*=3;

    }
    printf("%lld\n", ans);
}
