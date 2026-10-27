// category: conditionals  (real program 022)
// Codeforces submission 43958719, problem 1033/A, GNU C11, 2018-10-07
// https://codeforces.com/contest/1033/submission/43958719
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
    int n,Qx,Qy,Kx,Ky,Dx,Dy;
    scanf("%d",&n);
    scanf("%d %d",&Qx,&Qy);
    scanf("%d %d",&Kx,&Ky);
    scanf("%d %d",&Dx,&Dy);
    if(       (    Qx==n && Qy==1 ) || (Qx==n && Qy==n )||(Qx==1 && Qy==n ) ||  (Qx==1 && Qy==1 )       )
        printf("YES\n");
    else if(  Kx>Qx)
    {
        if(Ky<Qy)
        {
            if(Dx>Qx && Dy<Qy  )
                printf("YES\n");
            else
                printf("NO\n");
        }
        else
        {
            if(Dx>Qx && Dy>Qy  )
                printf("YES\n");
            else
                printf("NO\n");


        }


    }
    else if(Kx<Qx)
    {

        if(Ky<Qy)
        {
            if(Dx<Qx && Dy<Qy  )
                printf("YES\n");
            else
                printf("NO\n");
        }
        else
        {
            if(Dx<Qx && Dy>Qy  )
                printf("YES\n");
            else
                printf("NO\n");


        }



    }






return 0;
}
