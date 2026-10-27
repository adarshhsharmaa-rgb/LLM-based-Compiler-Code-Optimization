// category: mixed  (real program 039)
// Codeforces submission 21122936, problem 268/C, GNU C++11, 2016-10-02
// https://codeforces.com/contest/268/submission/21122936
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;

#define ll long long int



int main(){

    ll n,m,i,j;

    scanf("%lld %lld",&n,&m);

    if(n<m){

        printf("%lld\n",n+1);

        for(i=0;i<=n;i++){

            printf("%lld %lld\n",i,m-i);

        }

    }

    else{

        printf("%lld\n",m+1);

        for(i=0;i<=m;i++){

            printf("%lld %lld\n",n-i,i);

        }

    }



    return 0;

}
