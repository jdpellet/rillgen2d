#include<malloc.h>
#include<stdio.h>
#include<stdlib.h>
#include<math.h>

#define FREE_ARG char*
#define NR_END 1
#define stacksize 100000000
#define PI 3.1415926535897932
#define PIover4 0.78539816339744800
#define sqrt2 1.414213562373
#define oneoversqrt2 0.707106781186
#define large 1.e12
#define small 1.e-12
#define mfdweight 1.1

long count,*topovecind,*lakeis,*lakejs,*iup,*idown,*jup,*jdown,lattice_size_x,lattice_size_y,ic,jc;
int expansion,flagformask,flagford50,flagfortaucsoilandveg,flagforrain,flagforinfil,flagforcu,flagforthickness,flagforrockcover,**mask;
float threshslope,**rain,**infil,**d50,**cu,**thickness,**rockcover,**taucsoilandveg,**tau,**angle,**topo,**topo2,**slope,**area,flow1,flow2,flow3,flow4,flow5,flow6,flow7,flow8,*topovec;
float fillincrement,**f,**f2,slopex,slopey,deltax,yellowthreshold,rillwidth,reducedspecificgravity,rainfixed,infilfixed,b,c,d50fixed,rockcoverfixed,cufixed,thicknessfixed;
float taucsoilandvegfixed,**sinofslope,**cosofslopeterm,**taucarmor;

void free_lvector(long *v, long nl, long nh)
/* free an unsigned long vector allocated with lvector() */
{
	free((FREE_ARG) (v+nl-NR_END));
}

long *lvector(long nl, long nh)
/* allocate an unsigned long vector with subscript range v[nl..nh] */
{
	long *v;

	v=(long *)malloc((size_t) ((nh-nl+1+NR_END)*sizeof(long)));
	return v-nl+NR_END;
}

float *vector(long nl, long nh)
/* allocate an int vector with subscript range v[nl..nh] */
{
        float *v;

        v=(float *)malloc((size_t) ((nh-nl+1+NR_END)*sizeof(float)));
        return v-nl+NR_END;
}

float **matrix(long nrl, long nrh, long ncl, long nch)
/* allocate a float matrix with subscript range m[nrl..nrh][ncl..nch] */
{
	long i, nrow=nrh-nrl+1,ncol=nch-ncl+1;
	float **m;

	/* allocate pointers to rows */
	m=(float **) malloc((size_t)((nrow+NR_END)*sizeof(float*)));
	m += NR_END;
	m -= nrl;

	/* allocate rows and set pointers to them */
	m[nrl]=(float *) malloc((size_t)((nrow*ncol+NR_END)*sizeof(float)));
	m[nrl] += NR_END;
	m[nrl] -= ncl;

	for(i=nrl+1;i<=nrh;i++) m[i]=m[i-1]+ncol;

	/* return pointer to array of pointers to rows */
	return m;
}

int **imatrix(long nrl, long nrh, long ncl, long nch)
/* allocate a float matrix with subscript range m[nrl..nrh][ncl..nch] */
{
	long i, nrow=nrh-nrl+1,ncol=nch-ncl+1;
	int **m;

	/* allocate pointers to rows */
	m=(int **) malloc((size_t)((nrow+NR_END)*sizeof(int*)));
	m += NR_END;
	m -= nrl;

	/* allocate rows and set pointers to them */
	m[nrl]=(int *) malloc((size_t)((nrow*ncol+NR_END)*sizeof(int)));
	m[nrl] += NR_END;
	m[nrl] -= ncl;

	for(i=nrl+1;i<=nrh;i++) m[i]=m[i-1]+ncol;

	/* return pointer to array of pointers to rows */
	return m;
}

#define SWAP(a,b) itemp=(a);(a)=(b);(b)=itemp;
#define M 7
#define NSTACK 100000

void indexx(long n, float arr[], long indx[])
{
	long i,indxt,ir=n,itemp,j,k,l=1,jstack=0,*istack;
	float a;
	
        istack=lvector(1,NSTACK);
        for (j=1;j<=n;j++) indx[j]=j;
        for (;;) {
                if (ir-l < M) {
                        for (j=l+1;j<=ir;j++) {
                                indxt=indx[j];
                                a=arr[indxt];
                                for (i=j-1;i>=1;i--) {
                                        if (arr[indx[i]] <= a) break;
                                        indx[i+1]=indx[i];
                                }
                                indx[i+1]=indxt;
                        }
                        if (jstack == 0) break;
                        ir=istack[jstack--];
                        l=istack[jstack--];
                } else {
                        k=(l+ir) >> 1;
                        SWAP(indx[k],indx[l+1]);
                        if (arr[indx[l+1]] > arr[indx[ir]]) {
                                SWAP(indx[l+1],indx[ir])
                        }
                        if (arr[indx[l]] > arr[indx[ir]]) {
                                SWAP(indx[l],indx[ir])
                        }
                        if (arr[indx[l+1]] > arr[indx[l]]) {
                                SWAP(indx[l+1],indx[l])
                        }
                        i=l+1;
                        j=ir;
                        indxt=indx[l];
                        a=arr[indxt];
                        for (;;) {
                                do i++; while (arr[indx[i]] < a);
                                do j--; while (arr[indx[j]] > a);
                                if (j < i) break;
                                SWAP(indx[i],indx[j])
                        }
                        indx[l]=indx[j];
                        indx[j]=indxt;
                        jstack += 2;
                        if (ir-i+1 >= j-l) {
                                istack[jstack]=ir;
                                istack[jstack-1]=i;
                                ir=j-1;
                        } else {
                                istack[jstack]=j-1;
                                istack[jstack-1]=l;
                                l=i;
                        }
                }
        }
        free_lvector(istack,1,NSTACK);
}
#undef M
#undef NSTACK
#undef SWAP

void setupgridneighbors()
{    long i,j;

     idown=lvector(1,lattice_size_x);
     iup=lvector(1,lattice_size_x);
     jup=lvector(1,lattice_size_y);
     jdown=lvector(1,lattice_size_y);
     for (i=1;i<=lattice_size_x;i++)
      {idown[i]=i-1;
       iup[i]=i+1;}
     idown[1]=1;
     iup[lattice_size_x]=lattice_size_x;
     for (j=1;j<=lattice_size_y;j++)
      {jdown[j]=j-1;
       jup[j]=j+1;}
     jdown[1]=1;
     jup[lattice_size_y]=lattice_size_y;
}

void mfdflowroute(i,j)
long i,j;
{    float tot;

     if ((mask[i][j]==1)&&(slope[i][j]>threshslope)&&(i>1)&&(i<lattice_size_x)&&(j>1)&&(j<lattice_size_y))
	 {tot=0;
     if (topo[i][j]>topo[iup[i]][j])
      tot+=pow(topo[i][j]-topo[iup[i]][j],mfdweight);
     if (topo[i][j]>topo[idown[i]][j])
      tot+=pow(topo[i][j]-topo[idown[i]][j],mfdweight);
     if (topo[i][j]>topo[i][jup[j]])
      tot+=pow(topo[i][j]-topo[i][jup[j]],mfdweight);
     if (topo[i][j]>topo[i][jdown[j]])
      tot+=pow(topo[i][j]-topo[i][jdown[j]],mfdweight);
     if (topo[i][j]>topo[iup[i]][jup[j]])
      tot+=pow((topo[i][j]-topo[iup[i]][jup[j]])*oneoversqrt2,mfdweight);
     if (topo[i][j]>topo[iup[i]][jdown[j]])
      tot+=pow((topo[i][j]-topo[iup[i]][jdown[j]])*oneoversqrt2,mfdweight);
     if (topo[i][j]>topo[idown[i]][jup[j]])
      tot+=pow((topo[i][j]-topo[idown[i]][jup[j]])*oneoversqrt2,mfdweight);
     if (topo[i][j]>topo[idown[i]][jdown[j]])
      tot+=pow((topo[i][j]-topo[idown[i]][jdown[j]])*oneoversqrt2,mfdweight);
     if (topo[i][j]>topo[iup[i]][j])
      flow1=pow(topo[i][j]-topo[iup[i]][j],mfdweight)/tot;
       else flow1=0;
     if (topo[i][j]>topo[idown[i]][j])
      flow2=pow(topo[i][j]-topo[idown[i]][j],mfdweight)/tot;
       else flow2=0;
     if (topo[i][j]>topo[i][jup[j]])
      flow3=pow(topo[i][j]-topo[i][jup[j]],mfdweight)/tot;
       else flow3=0;
     if (topo[i][j]>topo[i][jdown[j]])
      flow4=pow(topo[i][j]-topo[i][jdown[j]],mfdweight)/tot;
       else flow4=0;
     if (topo[i][j]>topo[iup[i]][jup[j]])
      flow5=pow((topo[i][j]-topo[iup[i]][jup[j]])*oneoversqrt2,mfdweight)/tot;
       else flow5=0;
     if (topo[i][j]>topo[iup[i]][jdown[j]])
      flow6=pow((topo[i][j]-topo[iup[i]][jdown[j]])*oneoversqrt2,mfdweight)/tot;
       else flow6=0;
     if (topo[i][j]>topo[idown[i]][jup[j]])
      flow7=pow((topo[i][j]-topo[idown[i]][jup[j]])*oneoversqrt2,mfdweight)/tot;
       else flow7=0;
     if (topo[i][j]>topo[idown[i]][jdown[j]])
      flow8=pow((topo[i][j]-topo[idown[i]][jdown[j]])*oneoversqrt2,mfdweight)/tot;
       else flow8=0;
     area[iup[i]][j]+=area[i][j]*flow1;
     area[idown[i]][j]+=area[i][j]*flow2;
     area[i][jup[j]]+=area[i][j]*flow3;
     area[i][jdown[j]]+=area[i][j]*flow4;
     area[iup[i]][jup[j]]+=area[i][j]*flow5;
     area[iup[i]][jdown[j]]+=area[i][j]*flow6;
     area[idown[i]][jup[j]]+=area[i][j]*flow7;
     area[idown[i]][jdown[j]]+=area[i][j]*flow8;}
}

void push(i,j)
long i,j;
{  
	 count++;
     lakeis[count]=i;
     lakejs[count]=j;
}

void pop()
{  
     ic=lakeis[count];
     jc=lakejs[count];
	 count--;
}

void hydrologiccorrection()
{    long i,j;
     float max;

     count=0;
     for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   {push(i,j);
	    while (count>0) 
		 {pop();
		  max=topo[ic][jc];
          if (topo[iup[ic]][jc]<max) max=topo[iup[ic]][jc];
          if (topo[idown[ic]][jc]<max) max=topo[idown[ic]][jc];
          if (topo[ic][jup[jc]]<max) max=topo[ic][jup[jc]];
          if (topo[ic][jdown[jc]]<max) max=topo[ic][jdown[jc]];
	      if (topo[iup[ic]][jup[jc]]<max) max=topo[iup[ic]][jup[jc]];
          if (topo[idown[ic]][jdown[jc]]<max) max=topo[idown[ic]][jdown[jc]];
          if (topo[idown[ic]][jup[jc]]<max) max=topo[idown[ic]][jup[jc]];
          if (topo[iup[ic]][jdown[jc]]<max) max=topo[iup[ic]][jdown[jc]];
          if ((mask[ic][jc]==1)&&(topo[ic][jc]>0)&&(topo[ic][jc]<=max)&&(ic>1)&&(jc>1)&&(ic<lattice_size_x)&&(jc<lattice_size_y)&&(count<stacksize))
		   {topo[ic][jc]=max+fillincrement;
			push(ic,jc);
			push(iup[ic],jc);
			push(idown[ic],jc);
			push(ic,jup[jc]);
			push(ic,jdown[jc]);
	        push(iup[ic],jup[jc]);
			push(idown[ic],jdown[jc]);
			push(idown[ic],jup[jc]);
	        push(iup[ic],jdown[jc]);}}}
}

void setupgrids()
{
	 mask=imatrix(1,lattice_size_x,1,lattice_size_y);
	 topo=matrix(1,lattice_size_x,1,lattice_size_y);
	 topo2=matrix(1,lattice_size_x,1,lattice_size_y);
	 area=matrix(1,lattice_size_x,1,lattice_size_y);
	 f=matrix(1,lattice_size_x,1,lattice_size_y);
	 f2=matrix(1,lattice_size_x,1,lattice_size_y);
	 taucarmor=matrix(1,lattice_size_x,1,lattice_size_y);
	 taucsoilandveg=matrix(1,lattice_size_x,1,lattice_size_y);
	 tau=matrix(1,lattice_size_x,1,lattice_size_y);
	 sinofslope=matrix(1,lattice_size_x,1,lattice_size_y);
	 cosofslopeterm=matrix(1,lattice_size_x,1,lattice_size_y);
	 rain=matrix(1,lattice_size_x,1,lattice_size_y);
	 infil=matrix(1,lattice_size_x,1,lattice_size_y);
	 d50=matrix(1,lattice_size_x,1,lattice_size_y);
	 cu=matrix(1,lattice_size_x,1,lattice_size_y);
	 thickness=matrix(1,lattice_size_x,1,lattice_size_y);
	 rockcover=matrix(1,lattice_size_x,1,lattice_size_y);
	 slope=matrix(1,lattice_size_x,1,lattice_size_y);
	 topovec=vector(1,lattice_size_x*lattice_size_y);
	 topovecind=lvector(1,lattice_size_x*lattice_size_y);
	 lakeis=lvector(1,stacksize);
	 lakejs=lvector(1,stacksize);
}

void computecontributingarea()
{   long i,j,m;

	for (j=1;j<=lattice_size_y;j++)
     for (i=1;i<=lattice_size_x;i++)
	  {topovec[(j-1)*lattice_size_x+i]=topo[i][j];
	   area[i][j]=deltax*deltax;}
	indexx(lattice_size_x*lattice_size_y,topovec,topovecind);
	m=lattice_size_x*lattice_size_y+1;
	while (m>1)
	 {m--;
      i=(topovecind[m])%lattice_size_x;
      if (i==0) i=lattice_size_x;
      j=(topovecind[m])/lattice_size_x+1;
      if (i==lattice_size_x) j--;
	  mfdflowroute(i,j);}
}

int main()
{
     FILE *fpin,*fp0,*fp1,*fp2,*fp3,*fp4;
	 long i,j,m;
     
	 fpin=fopen("./input.txt","r");
	 fp0=fopen("./topo.txt","r");
	 fp1=fopen("./f.txt","w");
	 fp2=fopen("./rills.ppm","w");
	 fp3=fopen("./tau.txt","w");
	 fscanf(fpin,"%d",&flagformask);
	 fscanf(fpin,"%d",&flagforrain);
	 fscanf(fpin,"%d",&flagforinfil);
	 fscanf(fpin,"%d",&flagfortaucsoilandveg);
	 fscanf(fpin,"%d",&flagford50); 
	 fscanf(fpin,"%d",&flagforcu);
	 fscanf(fpin,"%d",&flagforthickness);
	 fscanf(fpin,"%d",&flagforrockcover);
	 fscanf(fpin,"%f",&fillincrement); 
	 fscanf(fpin,"%f",&threshslope); 
	 fscanf(fpin,"%d",&expansion); 
	 fscanf(fpin,"%f",&yellowthreshold); 
	 fscanf(fpin,"%ld",&lattice_size_x);
	 fscanf(fpin,"%ld",&lattice_size_y);
	 fscanf(fpin,"%f",&deltax);
     fscanf(fpin,"%f",&rainfixed);	 
	 fscanf(fpin,"%f",&infilfixed); 
	 fscanf(fpin,"%f",&taucsoilandvegfixed);
	 fscanf(fpin,"%f",&d50fixed);
	 fscanf(fpin,"%f",&cufixed);
     fscanf(fpin,"%f",&thicknessfixed);
     fscanf(fpin,"%f",&rockcoverfixed);  
	 fscanf(fpin,"%f",&reducedspecificgravity); 
	 fscanf(fpin,"%f",&b);
	 fscanf(fpin,"%f",&c);
     fscanf(fpin,"%f",&rillwidth);	 
	 setupgridneighbors();
	 setupgrids();
	 if (flagformask==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
		 mask[i][j]=1;} 
	  else 
	   {fp4=fopen("./mask.txt","r");
        for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
		  {fscanf(fp4,"%f",&mask[i][j]);
		   if (mask[i][j]>0) mask[i][j]=1;}
	    fclose(fp4);}
	 if (flagforrain==0)
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
	     rain[i][j]=rainfixed;}
	  else
       {fp4=fopen("./rain.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&rain[i][j]);
	    fclose(fp4);}
     if (flagforinfil==0)
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
	     infil[i][j]=infilfixed;}
	  else
       {fp4=fopen("./infil.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&infil[i][j]);
	    fclose(fp4);}		
	 if (flagfortaucsoilandveg==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
	     taucsoilandveg[i][j]=taucsoilandvegfixed;}
	  else
       {fp4=fopen("./taucsoilandveg.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&taucsoilandveg[i][j]);
	    fclose(fp4);}	
	 if (flagford50==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
		 d50[i][j]=d50fixed;} 
	  else 
	   {fp4=fopen("./d50.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&d50[i][j]);
	    fclose(fp4);}
	 if (flagforcu==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
		 cu[i][j]=cufixed;} 
	  else 
	   {fp4=fopen("./cu.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&cu[i][j]);
	    fclose(fp4);}
	 if (flagforthickness==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
		 thickness[i][j]=thicknessfixed;} 
	  else 
	   {fp4=fopen("./thickness.txt","r");
        thickness=matrix(1,lattice_size_x,1,lattice_size_y);
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&thickness[i][j]);
	    fclose(fp4);}
	 if (flagforrockcover==0) 
	  {for (j=1;j<=lattice_size_y;j++)
	    for (i=1;i<=lattice_size_x;i++)
	     rockcover[i][j]=rockcoverfixed;}
	  else
       {fp4=fopen("./rockcover.txt","r");
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp4,"%f",&rockcover[i][j]);
	    fclose(fp4);}
	 for (j=1;j<=lattice_size_y;j++)
	  for (i=1;i<=lattice_size_x;i++)
	   fscanf(fp0,"%f",&topo[i][j]);
     for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   {topo2[i][j]=topo[i][j];
        slopex=topo[iup[i]][j]-topo[idown[i]][j];
        slopey=topo[i][jup[j]]-topo[i][jdown[j]];
	    slope[i][j]=0.5*sqrt(slopex*slopex+slopey*slopey)/deltax;
		sinofslope[i][j]=sin(atan(slope[i][j]));
	    cosofslopeterm[i][j]=sqrt(9.81*cos(atan(slope[i][j])));}
	 hydrologiccorrection();
     computecontributingarea();
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   if (mask[i][j]==1)
	    {taucarmor[i][j]=9810*sinofslope[i][j]*pow(pow(pow(d50[i][j],0.38)*pow(cu[i][j],0.28)/(8.06*pow(thickness[i][j],0.62)*pow(slope[i][j],0.2)*1.16/pow(reducedspecificgravity,0.3)),4.76)/cosofslopeterm[i][j],0.666667);     
	     if (taucarmor[i][j]<taucsoilandveg[i][j]) taucarmor[i][j]=taucsoilandveg[i][j];
		 if ((rockcover[i][j]<0.99)&&(rockcover[i][j]>0.3)) taucarmor[i][j]/=exp(-4*(rockcover[i][j]-0.1));
		 tau[i][j]=(9810*sinofslope[i][j]*pow(b*(rain[i][j]-infil[i][j])/1000/3600*slope[i][j]*pow(area[i][j],c)/(rillwidth*cosofslopeterm[i][j]),0.666667));
		 f[i][j]=tau[i][j]/taucarmor[i][j];}
     for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   {if ((f[i][j]>0)&&(f[i][j]<=2)) fprintf(fp1,"%f\n",f[i][j]); else fprintf(fp1,"0.0\n"); 
		if (mask[i][j]==1) fprintf(fp3,"%f\n",tau[i][j]); else  fprintf(fp3,"0.0\n");}
     fprintf(fp2,"P3\n%d %d\n255\n",lattice_size_x,lattice_size_y);
	 for (m=1;m<=expansion;m++)
	  {for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
		 f2[i][j]=f[i][j];
	   for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
	     if ((f2[iup[i]][j]>=1)||(f2[idown[i]][j]>=1)||(f2[i][jup[j]]>=1)||(f2[i][jdown[j]]>=1)) f[i][j]=1.01;}
	 for (m=1;m<=expansion;m++)
	  {for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
		 f2[i][j]=f[i][j];
	   for (j=1;j<=lattice_size_y;j++)
        for (i=1;i<=lattice_size_x;i++)
	     if (((f2[iup[i]][j]>=yellowthreshold)&&(f2[i][j]<1))||((f2[idown[i]][j]>=yellowthreshold)&&(f2[idown[i]][j]<1))||((f2[i][jup[j]]>=yellowthreshold)&&(f2[i][jup[j]]<1))||((f2[i][jdown[j]]>=yellowthreshold)&&(f2[i][jdown[j]]<1))) f[i][j]=0.51;}
	 for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   if (mask[i][j]==0) fprintf(fp2,"0 0 0\n");
		else {if (f[i][j]>1) fprintf(fp2,"255 0 0\n"); else if (f[i][j]>yellowthreshold) fprintf(fp2,"255 255 0\n"); else fprintf(fp2,"255 255 255\n");}
}	   