#include<malloc.h>
#include<stdio.h>
#include<stdlib.h>
#include<math.h>

#define FREE_ARG char*
#define NR_END 1
#define stacksize 100000000
#define PI 3.1415926
#define sqrt2 1.414213562373
#define oneoversqrt2 0.707106781186
#define large 1.e^12

unsigned long count,*topovecind,*lakeis,*lakejs,*iup,*idown,*jup,*jdown,lattice_size_x,lattice_size_y,ic,jc;
int expansion,flagformask,flagford50,flagfortaucsoilandveg,**mask;
float threshslope,**d50grid,**taucsoilandveggrid,**topo,**topo2,**slope,**area,*topovec,flow1,flow2,flow3,flow4,flow5,flow6,flow7,flow8;
float fillincrement,**f,**f2,slopex,slopey,deltax,yellowthreshold,rillwidth,reducedspecificgravity,rain,infil,b,c,d50,rockcover,cu;
float thickness,taucsoilandveg,**sinofslope,**cosofslopeterm,**taucarmor;

void free_lvector(unsigned long *v, long nl, long nh)
/* free an unsigned long vector allocated with lvector() */
{
	free((FREE_ARG) (v+nl-NR_END));
}

unsigned long *lvector(long nl, long nh)
/* allocate an unsigned long vector with subscript range v[nl..nh] */
{
	unsigned long *v;

	v=(unsigned long *)malloc((size_t) ((nh-nl+1+NR_END)*sizeof(long)));
	return v-nl+NR_END;
}

float *vector(nl,nh)
long nh,nl;
/* allocate an int vector with subscript range v[nl..nh] */
{
        float *v;

        v=(float *)malloc((unsigned int) ((nh-nl+1+NR_END)*sizeof(float)));
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

void indexx(unsigned long n, float arr[], unsigned long indx[])
{
	unsigned long i,indxt,ir=n,itemp,j,k,l=1;
	long jstack=0,*istack;
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
{    unsigned long i,j;

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

void dinfflowroute(i,j)
unsigned long i,j;
{    float rmax,smax,max,s1,s2,r,s;

     rmax=0;smax=0;max=PI/4;
     s1=topo[i][j]-topo[i][jup[j]]; if (s1<0) s1=0;
	 s2=topo[i][jup[j]]-topo[idown[i]][jup[j]]; if (s2<0) s2=0;
	 r=atan(s2/s1);
	 s=sqrt(s1*s1+s2*s2);
     if (r<0) {r=0;s=s1;}
	 if (r>max) {r=max;s=(topo[i][j]-topo[idown[i]][jup[j]])/sqrt2;}
     if (s>smax) {smax=s;rmax=r;}
	 s1=topo[i][j]-topo[idown[i]][j]; if (s1<0) s1=0;
	 s2=topo[idown[i]][j]-topo[idown[i]][jup[j]];
	 r=atan(s2/s1);
	 s=sqrt(s1*s1+s2*s2);
     if (r<0) {r=0;s=s1;}
	 if (r>max) {r=max;s=(topo[i][j]-topo[idown[i]][jup[j]])/sqrt2;}
     if (s>smax) {smax=s;rmax=-r+PI/2;}
	 s1=topo[i][j]-topo[idown[i]][j]; if (s1<0) s1=0;
	 s2=topo[idown[i]][j]-topo[idown[i]][jdown[j]];
	 r=atan(s2/s1);
	 s=sqrt(s1*s1+s2*s2);
     if (r<0) {r=0;s=s1;}
	 if (r>max) {r=max;s=(topo[i][j]-topo[idown[i]][jdown[j]])/sqrt2;}
     if (s>smax) {smax=s;rmax=r+PI/2;}
     s1=topo[i][j]-topo[i][jdown[j]]; if (s1<0) s1=0;
	 s2=topo[i][jdown[j]]-topo[idown[i]][jdown[j]];
	 r=atan(s2/s1);
	 s=sqrt(s1*s1+s2*s2);
     if (r<0) {r=0;s=s1;}
	 if (r>max) {r=max;s=(topo[i][j]-topo[idown[i]][jdown[j]])/sqrt2;}
     if (s>smax) {smax=s;rmax=-r+PI;}
     s1=topo[i][j]-topo[i][jdown[j]]; if (s1<0) s1=0;
	 s2=topo[i][jdown[j]]-topo[iup[i]][jdown[j]];
	 r=atan(s2/s1);
	 s=sqrt(s1*s1+s2*s2);
     if (r<0) {r=0;s=s1;}
	 if (r>max) {r=max;s=(topo[i][j]-topo[iup[i]][jdown[j]])/sqrt2;}
     if (s>smax) {smax=s;rmax=r+PI;}
     s1=topo[i][j]-topo[iup[i]][j]; if (s1<0) s1=0;
	 s2=topo[iup[i]][j]-topo[iup[i]][jdown[j]];
	 r=atan(s2/s1);
	 s=sqrt(s1*s1+s2*s2);
     if (r<0) {r=0;s=s1;}
	 if (r>max) {r=max;s=(topo[i][j]-topo[iup[i]][jdown[j]])/sqrt2;}
     if (s>smax) {smax=s;rmax=-r+3*PI/2;}
     s1=topo[i][j]-topo[iup[i]][j]; if (s1<0) s1=0;
	 s2=topo[iup[i]][j]-topo[iup[i]][jup[j]];
	 r=atan(s2/s1);
	 s=sqrt(s1*s1+s2*s2);
     if (r<0) {r=0;s=s1;}
	 if (r>max) {r=max;s=(topo[i][j]-topo[iup[i]][jup[j]])/sqrt2;}
     if (s>smax) {smax=s;rmax=r+3*PI/2;}
     s1=topo[i][j]-topo[i][jup[j]]; if (s1<0) s1=0;
	 s2=topo[i][jup[j]]-topo[iup[i]][jup[j]];
	 r=atan(s2/s1);
	 s=sqrt(s1*s1+s2*s2);
     if (r<0) {r=0;s=s1;}
	 if (r>max) {r=max;s=(topo[i][j]-topo[iup[i]][jup[j]])/sqrt2;}
     if (s>smax) {smax=s;rmax=-r+2*PI;}
     r=rmax;
	 if (slope[i][j]<threshslope) area[i][j]=0;
	 if ((i>1)&&(i<lattice_size_x)&&(j>1)&&(j<lattice_size_y))
	  {if ((r>=0)&&(r<max)) {area[idown[i]][jup[j]]+=area[i][j]*r/max;area[i][jup[j]]+=area[i][j]*(max-r)/max;}
	   if ((r>=max)&&(r<2*max)) {area[idown[i]][j]+=area[i][j]*(r-max)/max;area[idown[i]][jup[j]]+=area[i][j]*(2*max-r)/max;}
	   if ((r>=2*max)&&(r<3*max)) {area[idown[i]][jdown[j]]+=area[i][j]*(r-2*max)/max;area[idown[i]][j]+=area[i][j]*(3*max-r)/max;}
	   if ((r>=3*max)&&(r<4*max)) {area[i][jdown[j]]+=area[i][j]*(r-3*max)/max;area[idown[i]][jdown[j]]+=area[i][j]*(4*max-r)/max;}
	   if ((r>=4*max)&&(r<5*max)) {area[iup[i]][jdown[j]]+=area[i][j]*(r-4*max)/max;area[i][jdown[j]]+=area[i][j]*(5*max-r)/max;}
	   if ((r>=5*max)&&(r<6*max)) {area[iup[i]][j]+=area[i][j]*(r-5*max)/max;area[iup[i]][jdown[j]]+=area[i][j]*(6*max-r)/max;}
	   if ((r>=6*max)&&(r<7*max)) {area[iup[i]][jup[j]]+=area[i][j]*(r-6*max)/max;area[iup[i]][j]+=area[i][j]*(7*max-r)/max;}
	   if ((r>=7*max)&&(r<8*max)) {area[i][jup[j]]+=area[i][j]*(r-7*max)/max;area[iup[i]][jup[j]]+=area[i][j]*(8*max-r)/max;}}
}

void push(i,j)
unsigned long i,j;
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
{    unsigned long i,j;
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
	 sinofslope=matrix(1,lattice_size_x,1,lattice_size_y);
	 cosofslopeterm=matrix(1,lattice_size_x,1,lattice_size_y);
	 slope=matrix(1,lattice_size_x,1,lattice_size_y);
	 topovec=vector(1,lattice_size_x*lattice_size_y);
	 topovecind=lvector(1,lattice_size_x*lattice_size_y);
	 lakeis=lvector(1,stacksize);
	 lakejs=lvector(1,stacksize);
}

void computecontributingarea()
{   unsigned long i,j,m;

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
	  if (mask[i][j]==1) dinfflowroute(i,j);}
}

main()
{
     FILE *fpin,*fp0,*fp1,*fp2,*fp3,*fp4,*fp5,*fp6,*fp7;
	 unsigned long i,j,m;
     
	 fpin=fopen("./input.txt","r");
	 fp0=fopen("./topo.txt","r");
	 fp1=fopen("./f.txt","w");
	 fp2=fopen("./rills.ppm","w");
	 fp3=fopen("./tau.txt","w");
	 fscanf(fpin,"%d",&flagformask); 
	 fscanf(fpin,"%d",&flagford50); 
	 fscanf(fpin,"%d",&flagfortaucsoilandveg); 
	 fscanf(fpin,"%f",&fillincrement); 
	 fscanf(fpin,"%f",&threshslope); 
	 fscanf(fpin,"%d",&expansion); 
	 fscanf(fpin,"%f",&yellowthreshold); 
	 fscanf(fpin,"%d",&lattice_size_x);
	 fscanf(fpin,"%d",&lattice_size_y);
	 fscanf(fpin,"%f",&deltax); 
	 fscanf(fpin,"%f",&rain); 
	 fscanf(fpin,"%f",&infil); 
	 fscanf(fpin,"%f",&cu);
     fscanf(fpin,"%f",&thickness);
     fscanf(fpin,"%f",&rockcover);  
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
	   {fp5=fopen("./mask.txt","r");
        for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
		  {fscanf(fp5,"%f",&mask[i][j]);
		   if (mask[i][j]>0) mask[i][j]=1;}
	    fclose(fp5);}
	 if (flagford50==0) fscanf(fpin,"%f",&d50); 
	  else 
	   {fp6=fopen("./d50.txt","r");
        d50grid=matrix(1,lattice_size_x,1,lattice_size_y);
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp6,"%f",&d50grid[i][j]);
	    fclose(fp6);}
     if (flagfortaucsoilandveg==0) fscanf(fpin,"%f",&taucsoilandveg); 
	  else
       {fp7=fopen("./taucsoilandveg.txt","r");
        taucsoilandveggrid=matrix(1,lattice_size_x,1,lattice_size_y);
		for (j=1;j<=lattice_size_y;j++)
	     for (i=1;i<=lattice_size_x;i++)
	      fscanf(fp7,"%f",&taucsoilandveggrid[i][j]);
	    fclose(fp7);}		  
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
	    {taucarmor[i][j]=9810*sinofslope[i][j]*pow(pow(pow(d50,0.38)*pow(cu,0.28)/(8.06*pow(thickness,0.62)*pow(slope[i][j],0.2)*1.16/pow(reducedspecificgravity,0.3)),4.76)/cosofslopeterm[i][j],0.666667);     
	     if (taucarmor[i][j]<taucsoilandveg) taucarmor[i][j]=taucsoilandveg;
		 if ((rockcover<0.99)&&(rockcover>0.3)) taucarmor[i][j]/=exp(-4*(rockcover-0.1));
		 f[i][j]=(9810*sinofslope[i][j]*pow(b*(rain-infil)/1000/3600*slope[i][j]*pow(area[i][j],c)/(rillwidth*cosofslopeterm[i][j]),0.666667))/taucarmor[i][j];}
     for (j=1;j<=lattice_size_y;j++)
      for (i=1;i<=lattice_size_x;i++)
	   {if ((f[i][j]>0)&&(f[i][j]<=2)) fprintf(fp1,"%f\n",f[i][j]); else fprintf(fp1,"0.0\n");
	    if (mask[i][j]==1) 
	     fprintf(fp3,"%f\n",(9810*sinofslope[i][j]*pow(b*(rain-infil)/1000/3600*slope[i][j]*pow(area[i][j],c)/(rillwidth*cosofslopeterm[i][j]),0.666667)));
	    else 
		 fprintf(fp3,"0.0\n");}
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
		else {if (f[i][j]>1) fprintf(fp2,"255 0 0\n"); else if (f[i][j]>0.5) fprintf(fp2,"255 255 0\n"); else fprintf(fp2,"255 255 255\n");}
}	   