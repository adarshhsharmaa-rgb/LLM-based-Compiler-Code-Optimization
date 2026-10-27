// category: loops  (real program 023)
// Codeforces submission 42176511, problem 1028/B, C++14 (GCC 6-32), 2018-08-27
// https://codeforces.com/contest/1028/submission/42176511
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<bits/stdc++.h>

using namespace std;

int main()  {
    for(int i = 1 ; i <= 300 ; ++i)
        printf("9");
    for(int i = 1 ; i <= 299 ; ++i)
        printf("0");
    printf("1\n");
    for(int i = 1 ; i <= 300 ; ++i)
        printf("9");
}
