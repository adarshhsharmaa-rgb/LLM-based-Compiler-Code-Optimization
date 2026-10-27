// category: loops  (real program 046)
// Codeforces submission 22140225, problem 622/A, GNU C++11, 2016-11-10
// https://codeforces.com/contest/622/submission/22140225
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<cstdio>  

#include <cstring>  

#include<cmath>  

#include<iostream>  

#include<algorithm>  

#include<vector>  

using namespace std;  

  

int main()  

{  

    long long n,i;  

    scanf("%I64d",&n);  

    i=0;  

    while(n>i)  

    {  

        n-=i;  

        i++;  

    }  

    printf("%I64d\n",n);  

}
