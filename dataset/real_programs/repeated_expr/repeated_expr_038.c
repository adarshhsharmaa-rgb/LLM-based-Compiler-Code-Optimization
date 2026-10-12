// category: repeated_expr  (real program 038)
// Codeforces submission 10684133, problem 534/A, GNU C, 2015-04-12
// https://codeforces.com/contest/534/submission/10684133
// from the dataset open-r1/codeforces-submissions (CC-BY-4.0)
#include<stdio.h>
int main()
{
	int i,n;
	//printf("Enter the no of students :");
	scanf("%d",&n);
	//int arr[n];
	if(n>=5)
	{
	printf("%d\n",n);
	if(n%2==0)
	{
		
	for(i=1;i<n;i+=2)
	printf("%d\t",i);
	for(i=2;i<=n;i+=2)
	printf("%d\t",i);
    }
    else if(n%2!=0)
    {
    	for(i=1;i<=n;i+=2)
    	printf("%d\t",i);
    	for(i=2;i<n;i+=2)
    	printf("%d\t",i);
	}
    }
    else if(n==1)
    {
    printf("%d\n",n);
    printf("%d",n);
}
    else if(n==2){
    printf("%d\n",n-1);
    printf("%d",n-1);
}
    else if(n==3){
    printf("%d\n",n-1);
    printf("%d %d",n-2,n);
}
    else if(n==4){
    printf("%d\n",n);
    printf("%d %d %d %d",n-1,n-3,n,n-2);
}
return 0;
}
