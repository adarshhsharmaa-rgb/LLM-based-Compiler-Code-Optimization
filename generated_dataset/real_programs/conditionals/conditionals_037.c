// category: conditionals  (real program 037)
// Codeforces submission 21376004, problem 622/B, C++14 (GCC 6-32), 2016-10-12
// https://codeforces.com/contest/622/submission/21376004
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include <bits/stdc++.h>

using namespace std;



int main()

{

    int H, n, M, d, r;



    scanf("%d : %d", &H, &M);

    scanf("%d", &n);

    d = n/60;

    r = n % 60;

    H+=d;

    M+=r;

    if(M>59){

        H++;

        M-=60;

    }

    if(H*60+M>=24*60){

        H%=24;

    }



    printf("%02d:%02d", H, M);

}
