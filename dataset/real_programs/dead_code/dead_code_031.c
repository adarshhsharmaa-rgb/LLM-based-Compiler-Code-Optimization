// category: dead_code  (real program 031)
// Codeforces submission 37961487, problem 1212/A, C++14 (GCC 6-32), 2018-05-06
// https://codeforces.com/contest/1212/submission/37961487
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
#include<cstdio>
#include<cstring>
#include<cstdlib>
#include<cctype>

#include<cmath>
#include<iostream>
#include<fstream>

#include<string>
#include<vector>
#include<queue>
#include<map>
#include<algorithm>
#include<set>
#include<sstream>
#include<stack>

using namespace std;


int main(){

    long long int a=0,b=0,c,d,i,j,n,m,ck=0;
    scanf("%lld %lld", &n, &a);

    for(i=1; i<=a; i++){
           b = n%10;
    if(b==0){
        n/=10;
    }else{
        n-=1;
    }
    }
    printf("%lld\n",n);
}
