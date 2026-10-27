// category: arithmetic  (real program 012)
// Codeforces submission 39628467, problem 996/A, C++17 (GCC 7-32), 2018-06-24
// https://codeforces.com/contest/996/submission/39628467
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;
int main()
{
    
    int n,res=0;
    
    scanf("%d",&n);
    
    res+=(n/100);n%=100;
    
    res+=(n/20);n%=20;
    
    res+=(n/10);n%=10;
    
    res+=(n/5);n%=5;
    
    res+=(n/1);n%=1;
    
    printf("%d\n",res);
    
    return 0;
    
}
