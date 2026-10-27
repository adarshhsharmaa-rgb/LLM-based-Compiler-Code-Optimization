// category: nested  (real program 038)
// Codeforces submission 39621984, problem 996/A, C++14 (GCC 6-32), 2018-06-24
// https://codeforces.com/contest/996/submission/39621984
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>
using namespace std;

int main(){

    int a, b, c, d,e,f,g,h,n, i, j,k;
    scanf("%d", &n );
    a = n / 100;
    b = n - a*100;
    c = b / 20;
    d = b - c*20;
    e = d / 10 ;
    f = d - e*10;
    g = f / 5 ;
    h = f - g*5;
    i = h / 1 ;
    k = a + c + e + g + i;
    printf("%d\n", k ) ;



    return 0;
}
