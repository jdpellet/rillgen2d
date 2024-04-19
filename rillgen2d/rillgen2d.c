#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define FREE_ARG char *
#define NR_END 1

#define PI 3.1415926535897932
#define PIover4 0.78539816339744800
#define sqrt2 1.414213562373
#define oneoversqrt2 0.707106781186
#define large 1.e12
#define tiny 1.e-12
#define small 1.e-6
#define mfdweight 1.1
#define tenthirdstimesmfdweight 3.6666666666667
#define twicemfdweight 2.2
#define fivethirds 1.666666666666667

long t, *topovecind;
int flagformode, flagforroutingmethod, numberofraindata, numberofraingages, **closestgage, **nextclosestgage, expansion, smoothinglength, numberofdatapoints;
int flagforshearstressequation, flagformode, flagformask, flagforslope, flagford50, flagfortaucsoilandveg, flagforrain, flagforthickness, flagforrockcover, **mask, flagforrockthickness, numberofslices, numberofsweeps;
int **i1, **jl, **i2, **j2, *iup, *idown, *jup, *jdown, lattice_size_x, lattice_size_y, ic, jc;
double weightfactor, manningsn, excessshearstress, rillwidth, nodatavalue, oneoverdeltax, durationofdata, timestep, ulx, uly, *raingagex;
double oneminusweightfactor, *raingagey, **sinofslope, **angle, rillwidthcoefficient, rillwidthexponent, dist, *rainvalues, durationofdata;
double minslope, **slopefactor, **discharge, **rainl, **rain, **d50, **cu, **thickness, **rockcover, **taucsoilandveg, **tau;
double anglel, **topo, **slope, **area, **depth, **discharge, flowl1, flowl2, flow1, flow2, flow3, flow4, flow5, flow6, flow7, flow8;
double *topovec, fillincrement, **inciseddepth, **f1, **f2, deltax, yellowthreshold, rainfixed, b, c, d50fixed, rockcoverfixed, bulkdensity;
double incisionincrement, slopex, slopey, timescaleofinterest, durationofdata, rillerodibilitycoefficient, rillerodibilityexponent, tanangleofinternalfriction;
double taucsoilandvegfixed, **cosofslopeterm, **taucarmor, **topoorig, coverthicknessfixed, sumarea, **depthold, rockthicknessfixed, **rockthickness, **eroded, sumerosion;
double **maxtau, dischargel, f1l, f2l, **distancetoclosestgage, **distancetonextclosestgage;

void free_ivector(int *v, int nl, int nh)
/* free an int vector allocated with ivector() */
{
	free((FREE_ARG)(v + nl - NR_END));
}

void free_vector(double *v, int nl, int nh)
/* free a double vector allocated with vector() */
{
	free((FREE_ARG)(v + nl - NR_END));
}

void free_lvector(long *v, long nl, long nh)
/* free an unsigned long vector allocated with lvector() */
{
	free((FREE_ARG)(v + nl - NR_END));
}

void free_matrix(double **m, int nrl, int nrh, int ncl, int nch)
/* free a double matrix allocated by matrix() */
{
	free((FREE_ARG)(m[nrl] + ncl - NR_END));
	free((FREE_ARG)(m + nrl - NR_END));
}

void free_imatrix(int **m, int nrl, int nrh, int ncl, int nch)
/* free an int matrix allocated by imatrix() */
{
	free((FREE_ARG)(m[nrl] + ncl - NR_END));
	free((FREE_ARG)(m + nrl - NR_END));
}

long *lvector(long nl, long nh)
/* allocate an unsigned long vector with subscript range v[nl..nh] */
{
	long *v;

	v = (long *)malloc((size_t)((nh - nl + 1 + NR_END) * sizeof(long)));
	return v - nl + NR_END;
}

int *ivector(int nl, int nh)
/* allocate an int vector with subscript range v[nl..nh] */
{
	int *v;

	v = (int *)malloc((size_t)((nh - nl + 1 + NR_END) * sizeof(int)));
	return v - nl + NR_END;
}

double *vector(int nl, int nh)
/* allocate an int vector with subscript range v[nl..nh] */
{
	double *v;

	v = (double *)malloc((size_t)((nh - nl + 1 + NR_END) * sizeof(double)));
	return v - nl + NR_END;
}

double **matrix(int nrl, int nrh, int ncl, int nch)
/* allocate a double matrix with subscript range m[nrl..nrh][ncl..nch] */
{
	int i, nrow = nrh - nrl + 1, ncol = nch - ncl + 1;
	double **m;

	/* allocate pointers to rows */
	m = (double **)malloc((size_t)((nrow + NR_END) * sizeof(double *)));
	m += NR_END;
	m -= nrl;

	/* allocate rows and set pointers to them */
	m[nrl] = (double *)malloc((size_t)((nrow * ncol + NR_END) * sizeof(double)));
	m[nrl] += NR_END;
	m[nrl] -= ncl;

	for (i = nrl + 1; i <= nrh; i++)
		m[i] = m[i - 1] + ncol;

	/* return pointer to array of pointers to rows */
	return m;
}

int **imatrix(int nrl, int nrh, int ncl, int nch)
/* allocate a double matrix with subscript range m[nrl..nrh][ncl..nch] */
{
	int i, nrow = nrh - nrl + 1, ncol = nch - ncl + 1;
	int **m;

	/* allocate pointers to rows */
	m = (int **)malloc((size_t)((nrow + NR_END) * sizeof(int *)));
	m += NR_END;
	m -= nrl;

	/* allocate rows and set pointers to them */
	m[nrl] = (int *)malloc((size_t)((nrow * ncol + NR_END) * sizeof(int)));
	m[nrl] += NR_END;
	m[nrl] -= ncl;

	for (i = nrl + 1; i <= nrh; i++)
		m[i] = m[i - 1] + ncol;

	/* return pointer to array of pointers to rows */
	return m;
}

#define SWAP(a, b) \
	itemp = (a);   \
	(a) = (b);     \
	(b) = itemp;
#define M 7
#define NSTACK 100000

void indexx(long n, double arr[], long indx[])
{
	long i, indxt, ir = n, itemp, j, k, l = 1, jstack = 0, *istack;
	double a;

	istack = lvector(1, NSTACK);
	for (j = 1; j <= n; j++)
		indx[j] = j;
	for (;;)
	{
		if (ir - l < M)
		{
			for (j = l + 1; j <= ir; j++)
			{
				indxt = indx[j];
				a = arr[indxt];
				for (i = j - 1; i >= 1; i--)
				{
					if (arr[indx[i]] <= a)
						break;
					indx[i + 1] = indx[i];
				}
				indx[i + 1] = indxt;
			}
			if (jstack == 0)
				break;
			ir = istack[jstack--];
			l = istack[jstack--];
		}
		else
		{
			k = (l + ir) >> 1;
			SWAP(indx[k], indx[l + 1]);
			if (arr[indx[l + 1]] > arr[indx[ir]])
			{
				SWAP(indx[l + 1], indx[ir])
			}
			if (arr[indx[l]] > arr[indx[ir]])
			{
				SWAP(indx[l], indx[ir])
			}
			if (arr[indx[l + 1]] > arr[indx[l]])
			{
				SWAP(indx[l + 1], indx[l])
			}
			i = l + 1;
			j = ir;
			indxt = indx[l];
			a = arr[indxt];
			for (;;)
			{
				do
					i++;
				while (arr[indx[i]] < a);
				do
					j--;
				while (arr[indx[j]] > a);
				if (j < i)
					break;
				SWAP(indx[i], indx[j])
			}
			indx[l] = indx[j];
			indx[j] = indxt;
			jstack += 2;
			if (ir - i + 1 >= j - l)
			{
				istack[jstack] = ir;
				istack[jstack - 1] = i;
				ir = j - 1;
			}
			else
			{
				istack[jstack] = j - 1;
				istack[jstack - 1] = l;
				l = i;
			}
		}
	}
	free_lvector(istack, 1, NSTACK);
}
#undef M
#undef NSTACK
#undef SWAP

void setupgridneighbors()
{
	int i, j;

	idown = ivector(1, lattice_size_x);
	iup = ivector(1, lattice_size_x);
	jup = ivector(1, lattice_size_y);
	jdown = ivector(1, lattice_size_y);
	for (i = 1; i <= lattice_size_x; i++)
	{
		idown[i] = i - 1;
		iup[i] = i + 1;
	}
	idown[1] = 1;
	iup[lattice_size_x] = lattice_size_x;
	for (j = 1; j <= lattice_size_y; j++)
	{
		jdown[j] = j - 1;
		jup[j] = j + 1;
	}
	jdown[1] = 1;
	jup[lattice_size_y] = lattice_size_y;
}

int flat_index(int i, int j)
{
	return (j - 1) * lattice_size_x + i;
}

/* priority flood algorithm */
int I;
#define SWAP(a, b) \
	itemp = (a);   \
	(a) = (b);     \
	(b) = itemp;
#define DSWAP(a, b) \
	dtemp = (a);    \
	(a) = (b);      \
	(b) = dtemp;

void bubble_up(int *pqueue, double *pval, int k)
{
	/* Bubble the queue entry at index k up the binary heap until order is valid */
	int itemp, parent, i;
	double dtemp;
	i = k;
	while (i > 1)
	{
		parent = i / 2;				// note floor division
		if (pval[i] < pval[parent]) // heap-order is broken
		{
			SWAP(pqueue[i], pqueue[parent]);
			DSWAP(pval[i], pval[parent]);
			i = parent;
		}
		else // heap-order is valid
			break;
	}
}
#undef SWAP
#undef DSWAP

void bubble_emptyroot(int *pqueue, double *pval)
{
	/* Bubbles empty root down to a leaf node, swaps with last queue entry, bubbles up swapped entry to restore heap order */
	int lchild, rchild, smallest, i = 1;
	while (i <= I / 2)
	{ // simpler bubble down, only 1 comparison per iter
		lchild = 2 * i;
		rchild = 2 * i + 1;
		if (rchild <= I && pval[rchild] <= pval[lchild])
			smallest = rchild;
		else
			smallest = lchild;
		pqueue[i] = pqueue[smallest];
		pval[i] = pval[smallest];
		i = smallest;
	} // upon exit, i is index of a leaf node
	if (i < I)
	{
		pqueue[i] = pqueue[I];
		pval[i] = pval[I];
		I--;
		bubble_up(pqueue, pval, i);
	}
	else // empty root landed at the final entry of the queue; nothing to do but decrement size
		I--;
}

void pf_push(int *pqueue, double *pval, int t)
{
	/* Add an element to the end of the heap and restore heap-order property */
	I++;
	if (I > lattice_size_x * lattice_size_y)
	{
		fprintf(stderr, "The priority queue is full, something went wrong\n");
		exit(EXIT_FAILURE);
	}
	pqueue[I] = t;
	pval[I] = topovec[t];
	/* Bubble up */
	bubble_up(pqueue, pval, I);
}

int pf_pop(int *pqueue, double *pval)
{
	/* Pops off the root (guaranteed to be minimum topography in the binary heap) and restores the heap-order property */
	int troot;
	troot = pqueue[1]; // pop current root
	/* Bubble empty root down to restore heap-order; slightly more efficient than generic bubble-down alg (~log2+k vs ~2*log2) */
	bubble_emptyroot(pqueue, pval);
	return troot;
}

void priority_flood_epsilon()
{
	/* Fill pits and flats with priority-flood + epsilon */
	int i, j, t, tn, k;
	int **closed, *pqueue, neighboris[8], neighborjs[8];
	double *pval;

	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			topovec[flat_index(i, j)] = topo[i][j];

	/* initialize binary heap, will be used as priority queue with time complexity ~O(n*log[n]) */
	closed = imatrix(1, lattice_size_x, 1, lattice_size_y);
	pqueue = ivector(1, lattice_size_x * lattice_size_y); // this should be the maximum size and I doubt it will ever get close to it (unless the entire DEM is a pit!)
	pval = vector(1, lattice_size_x * lattice_size_y);
	I = 0;
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			closed[i][j] = 0;
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			if (mask[i][j] == 0)
			{
				t = flat_index(i, j);
				pf_push(pqueue, pval, t);
				closed[i][j] = 1;
			}
	/* Iterate while the priority queue is not empty */
	while (I > 0)
	{
		/* pop the root of the queue */
		t = pf_pop(pqueue, pval);
		i = t % lattice_size_x;
		if (i == 0)
			i = lattice_size_x;
		j = t / lattice_size_x + 1;
		if (i == lattice_size_x)
			j--;
		/* for each neighbor of popped node, fill and push to queue if not already closed */
		neighboris[0] = idown[i];
		neighboris[1] = iup[i];
		neighboris[2] = i;
		neighboris[3] = i;
		neighboris[4] = idown[i];
		neighboris[5] = idown[i];
		neighboris[6] = iup[i];
		neighboris[7] = iup[i];
		neighborjs[0] = j;
		neighborjs[1] = j;
		neighborjs[2] = jdown[j];
		neighborjs[3] = jup[j];
		neighborjs[4] = jdown[j];
		neighborjs[5] = jup[j];
		neighborjs[6] = jdown[j];
		neighborjs[7] = jup[j];
		for (k = 0; k < 8; k++)
		{
			if (closed[neighboris[k]][neighborjs[k]] != 1)
			{
				tn = flat_index(neighboris[k], neighborjs[k]);
				if (topovec[tn] <= topovec[t] && mask[neighboris[k]][neighborjs[k]] == 1) // neighbor's a pit!
					topovec[tn] = topovec[t] + fillincrement;							  // we fill it to ensure it drains
				closed[neighboris[k]][neighborjs[k]] = 1;
				pf_push(pqueue, pval, tn);
			}
		}
	}
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			topo[i][j] = topovec[flat_index(i, j)];
	free_imatrix(closed, 1, lattice_size_x, 1, lattice_size_y);
	free_ivector(pqueue, 1, lattice_size_x * lattice_size_y);
	free_vector(pval, 1, lattice_size_x * lattice_size_y);
}

void smoothslope()
{
	int i, j, i2, j2, il, jl;
	int n, **countslope;
	double **sumslope;

	sumslope = matrix(1, lattice_size_x, 1, lattice_size_y);
	countslope = imatrix(1, lattice_size_x, 1, lattice_size_y);
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
		{
			sumslope[i][j] = 0;
			countslope[i][j] = 0;
		}
	j = smoothinglength / 2;
	for (i = 1; i <= lattice_size_x; i++)
		for (j2 = j - smoothinglength / 2; j2 <= j + smoothinglength / 2; j2++)
			for (i2 = i - smoothinglength / 2; i2 <= i + smoothinglength / 2; i2++)
			{
				il = i;
				jl = j;
				if (i2 < i)
					for (n = 1; n <= i - i2; n++)
						il = idown[il];
				else
					for (n = 1; n <= i2 - i; n++)
						il = iup[il];
				if (j2 < j)
					for (n = 1; n <= j - j2; n++)
						jl = jdown[jl];
				else
					for (n = 1; n <= j2 - j; n++)
						jl = jup[jl];
				if (mask[il][jl] == 1)
				{
					sumslope[i][j] += slope[il][jl];
					countslope[i][j]++;
				}
			}
	j = lattice_size_y - smoothinglength / 2;
	for (i = 1; i <= lattice_size_x; i++)
		for (j2 = j - smoothinglength / 2; j2 <= j + smoothinglength / 2; j2++)
			for (i2 = i - smoothinglength / 2; i2 <= i + smoothinglength / 2; i2++)
			{
				il = i;
				jl = j;
				if (i2 < i)
					for (n = 1; n <= i - i2; n++)
						il = idown[il];
				else
					for (n = 1; n <= i2 - i; n++)
						il = iup[il];
				if (j2 < j)
					for (n = 1; n <= j - j2; n++)
						jl = jdown[jl];
				else
					for (n = 1; n <= j2 - j; n++)
						jl = jup[jl];
				if (mask[il][jl] == 1)
				{
					sumslope[i][j] += slope[il][jl];
					countslope[i][j]++;
				}
			}
	i = smoothinglength / 2;
	for (j = 1; j <= lattice_size_y; j++)
		for (j2 = j - smoothinglength / 2; j2 <= j + smoothinglength / 2; j2++)
			for (i2 = i - smoothinglength / 2; i2 <= i + smoothinglength / 2; i2++)
			{
				il = i;
				jl = j;
				if (i2 < i)
					for (n = 1; n <= i - i2; n++)
						il = idown[il];
				else
					for (n = 1; n <= i2 - i; n++)
						il = iup[il];
				if (j2 < j)
					for (n = 1; n <= j - j2; n++)
						jl = jdown[jl];
				else
					for (n = 1; n <= j2 - j; n++)
						jl = jup[jl];
				if (mask[il][jl] == 1)
				{
					sumslope[i][j] += slope[il][jl];
					countslope[i][j]++;
				}
			}
	i = lattice_size_x - smoothinglength / 2;
	for (j = 1; j <= lattice_size_y; j++)
		for (j2 = j - smoothinglength / 2; j2 <= j + smoothinglength / 2; j2++)
			for (i2 = i - smoothinglength / 2; i2 <= i + smoothinglength / 2; i2++)
			{
				il = i;
				jl = j;
				if (i2 < i)
					for (n = 1; n <= i - i2; n++)
						il = idown[il];
				else
					for (n = 1; n <= i2 - i; n++)
						il = iup[il];
				if (j2 < j)
					for (n = 1; n <= j - j2; n++)
						jl = jdown[jl];
				else
					for (n = 1; n <= j2 - j; n++)
						jl = jup[jl];
				if (mask[il][jl] == 1)
				{
					sumslope[i][j] += slope[il][jl];
					countslope[i][j]++;
				}
			}
	for (j = smoothinglength / 2 + 1; j < lattice_size_y - smoothinglength / 2; j++)
	{
		for (i = smoothinglength / 2 + 1; i < lattice_size_x - smoothinglength / 2; i++)
		{
			sumslope[i][j] = sumslope[idown[i]][j];
			countslope[i][j] = countslope[idown[i]][j];
			for (j2 = -smoothinglength / 2; j2 <= smoothinglength / 2; j2++)
			{
				if (mask[i - smoothinglength / 2][j + j2] == 1)
				{
					sumslope[i][j] -= slope[i - smoothinglength / 2][j + j2];
					countslope[i][j]--;
				}
				if (mask[i + smoothinglength / 2][j + j2] == 1)
				{
					sumslope[i][j] += slope[i + smoothinglength / 2][j + j2];
					countslope[i][j]++;
				}
			}
		}
		i = smoothinglength / 2 + 1;
	}
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			if (countslope[i][j] > (smoothinglength * smoothinglength / 2))
				slope[i][j] = sumslope[i][j] / countslope[i][j];
	free_matrix(sumslope, 1, lattice_size_x, 1, lattice_size_y);
	free_imatrix(countslope, 1, lattice_size_x, 1, lattice_size_y);
}

void dinfflowrouteorig(int i, int j)
{
	double rmax, smax, s1, s2, r, s, diff;

	rmax = 0;
	smax = 0;
	s1 = topo[i][j] - topo[i][jup[j]];
	if (s1 < 0)
		s1 = 0;
	s2 = topo[i][jup[j]] - topo[idown[i]][jup[j]];
	if (s2 < 0)
		s2 = 0;
	r = atan(s2 / s1);
	s = sqrt(s1 * s1 + s2 * s2);
	if (r < 0)
	{
		r = 0;
		s = s1;
	}
	if (r > PIover4)
	{
		r = PIover4;
		s = (topo[i][j] - topo[idown[i]][jup[j]]) * oneoversqrt2;
	}
	if (s > smax)
	{
		smax = s;
		rmax = r;
	}
	s1 = topo[i][j] - topo[idown[i]][j];
	if (s1 < 0)
		s1 = 0;
	s2 = topo[idown[i]][j] - topo[idown[i]][jup[j]];
	r = atan(s2 / s1);
	s = sqrt(s1 * s1 + s2 * s2);
	if (r < 0)
	{
		r = 0;
		s = s1;
	}
	if (r > PIover4)
	{
		r = PIover4;
		s = (topo[i][j] - topo[idown[i]][jup[j]]) * oneoversqrt2;
	}
	if (s > smax)
	{
		smax = s;
		rmax = -r + PI / 2;
	}
	s1 = topo[i][j] - topo[idown[i]][j];
	if (s1 < 0)
		s1 = 0;
	s2 = topo[idown[i]][j] - topo[idown[i]][jdown[j]];
	r = atan(s2 / s1);
	s = sqrt(s1 * s1 + s2 * s2);
	if (r < 0)
	{
		r = 0;
		s = s1;
	}
	if (r > PIover4)
	{
		r = PIover4;
		s = (topo[i][j] - topo[idown[i]][jdown[j]]) * oneoversqrt2;
	}
	if (s > smax)
	{
		smax = s;
		rmax = r + PI / 2;
	}
	s1 = topo[i][j] - topo[i][jdown[j]];
	if (s1 < 0)
		s1 = 0;
	s2 = topo[i][jdown[j]] - topo[idown[i]][jdown[j]];
	r = atan(s2 / s1);
	s = sqrt(s1 * s1 + s2 * s2);
	if (r < 0)
	{
		r = 0;
		s = s1;
	}
	if (r > PIover4)
	{
		r = PIover4;
		s = (topo[i][j] - topo[idown[i]][jdown[j]]) * oneoversqrt2;
	}
	if (s > smax)
	{
		smax = s;
		rmax = -r + PI;
	}
	s1 = topo[i][j] - topo[i][jdown[j]];
	if (s1 < 0)
		s1 = 0;
	s2 = topo[i][jdown[j]] - topo[iup[i]][jdown[j]];
	r = atan(s2 / s1);
	s = sqrt(s1 * s1 + s2 * s2);
	if (r < 0)
	{
		r = 0;
		s = s1;
	}
	if (r > PIover4)
	{
		r = PIover4;
		s = (topo[i][j] - topo[iup[i]][jdown[j]]) * oneoversqrt2;
	}
	if (s > smax)
	{
		smax = s;
		rmax = r + PI;
	}
	s1 = topo[i][j] - topo[iup[i]][j];
	if (s1 < 0)
		s1 = 0;
	s2 = topo[iup[i]][j] - topo[iup[i]][jdown[j]];
	r = atan(s2 / s1);
	s = sqrt(s1 * s1 + s2 * s2);
	if (r < 0)
	{
		r = 0;
		s = s1;
	}
	if (r > PIover4)
	{
		r = PIover4;
		s = (topo[i][j] - topo[iup[i]][jdown[j]]) * oneoversqrt2;
	}
	if (s > smax)
	{
		smax = s;
		rmax = -r + 3 * PI / 2;
	}
	s1 = topo[i][j] - topo[iup[i]][j];
	if (s1 < 0)
		s1 = 0;
	s2 = topo[iup[i]][j] - topo[iup[i]][jup[j]];
	r = atan(s2 / s1);
	s = sqrt(s1 * s1 + s2 * s2);
	if (r < 0)
	{
		r = 0;
		s = s1;
	}
	if (r > PIover4)
	{
		r = PIover4;
		s = (topo[i][j] - topo[iup[i]][jup[j]]) * oneoversqrt2;
	}
	if (s > smax)
	{
		smax = s;
		rmax = r + 3 * PI / 2;
	}
	s1 = topo[i][j] - topo[i][jup[j]];
	if (s1 < 0)
		s1 = 0;
	s2 = topo[i][jup[j]] - topo[iup[i]][jup[j]];
	r = atan(s2 / s1);
	s = sqrt(s1 * s1 + s2 * s2);
	if (r < 0)
	{
		r = 0;
		s = s1;
	}
	if (r > PIover4)
	{
		r = PIover4;
		s = (topo[i][j] - topo[iup[i]][jup[j]]) * oneoversqrt2;
	}
	if (s > smax)
	{
		smax = s;
		rmax = -r + 2 * PI;
	}
	r = rmax;
	if ((mask[i][j] == 1) && (slope[i][j] > minslope) && (i > 1) && (i < lattice_size_x) && (j > 1) && (j < lattice_size_y))
	{
		if ((r >= 0) && (r < PIover4))
		{
			diff = r / PIover4;
			area[idown[i]][jup[j]] += area[i][j] * diff;
			area[i][jup[j]] += area[i][j] * (1 - diff);
		}
		if ((r >= PIover4) && (r < 2 * PIover4))
		{
			diff = r / PIover4 - 1;
			area[idown[i]][j] += area[i][j] * diff;
			area[idown[i]][jup[j]] += area[i][j] * (1 - diff);
		}
		if ((r >= 2 * PIover4) && (r < 3 * PIover4))
		{
			diff = r / PIover4 - 2;
			area[idown[i]][jdown[j]] += area[i][j] * diff;
			area[idown[i]][j] += area[i][j] * (1 - diff);
		}
		if ((r >= 3 * PIover4) && (r < 4 * PIover4))
		{
			diff = r / PIover4 - 3;
			area[i][jdown[j]] += area[i][j] * diff;
			area[idown[i]][jdown[j]] += area[i][j] * (1 - diff);
		}
		if ((r >= 4 * PIover4) && (r < 5 * PIover4))
		{
			diff = r / PIover4 - 4;
			area[iup[i]][jdown[j]] += area[i][j] * diff;
			area[i][jdown[j]] += area[i][j] * (1 - diff);
		}
		if ((r >= 5 * PIover4) && (r < 6 * PIover4))
		{
			diff = r / PIover4 - 5;
			area[iup[i]][j] += area[i][j] * diff;
			area[iup[i]][jdown[j]] += area[i][j] * (1 - diff);
		}
		if ((r >= 6 * PIover4) && (r < 7 * PIover4))
		{
			diff = r / PIover4 - 6;
			area[iup[i]][jup[j]] += area[i][j] * diff;
			area[iup[i]][j] += area[i][j] * (1 - diff);
		}
		if ((r >= 7 * PIover4) && (r < 8 * PIover4))
		{
			diff = r / PIover4 - 7;
			area[i][jup[j]] += area[i][j] * diff;
			area[iup[i]][jup[j]] += area[i][j] * (1 - diff);
		}
	}
}

void mfdflowrouteorig(int i, int j)
{
	double tot;

	if ((mask[i][j] == 1) && (slope[i][j] > minslope) && (i > 1) && (i < lattice_size_x) && (j > 1) && (j < lattice_size_y))
	{
		tot = 0;
		if (topo[i][j] > topo[iup[i]][j])
			tot += pow(topo[i][j] - topo[iup[i]][j], mfdweight);
		if (topo[i][j] > topo[idown[i]][j])
			tot += pow(topo[i][j] - topo[idown[i]][j], mfdweight);
		if (topo[i][j] > topo[i][jup[j]])
			tot += pow(topo[i][j] - topo[i][jup[j]], mfdweight);
		if (topo[i][j] > topo[i][jdown[j]])
			tot += pow(topo[i][j] - topo[i][jdown[j]], mfdweight);
		if (topo[i][j] > topo[iup[i]][jup[j]])
			tot += pow((topo[i][j] - topo[iup[i]][jup[j]]) * oneoversqrt2, mfdweight);
		if (topo[i][j] > topo[iup[i]][jdown[j]])
			tot += pow((topo[i][j] - topo[iup[i]][jdown[j]]) * oneoversqrt2, mfdweight);
		if (topo[i][j] > topo[idown[i]][jup[j]])
			tot += pow((topo[i][j] - topo[idown[i]][jup[j]]) * oneoversqrt2, mfdweight);
		if (topo[i][j] > topo[idown[i]][jdown[j]])
			tot += pow((topo[i][j] - topo[idown[i]][jdown[j]]) * oneoversqrt2, mfdweight);
		if (topo[i][j] > topo[iup[i]][j])
			flow1 = pow(topo[i][j] - topo[iup[i]][j], mfdweight) / tot;
		else
			flow1 = 0;
		if (topo[i][j] > topo[idown[i]][j])
			flow2 = pow(topo[i][j] - topo[idown[i]][j], mfdweight) / tot;
		else
			flow2 = 0;
		if (topo[i][j] > topo[i][jup[j]])
			flow3 = pow(topo[i][j] - topo[i][jup[j]], mfdweight) / tot;
		else
			flow3 = 0;
		if (topo[i][j] > topo[i][jdown[j]])
			flow4 = pow(topo[i][j] - topo[i][jdown[j]], mfdweight) / tot;
		else
			flow4 = 0;
		if (topo[i][j] > topo[iup[i]][jup[j]])
			flow5 = pow((topo[i][j] - topo[iup[i]][jup[j]]) * oneoversqrt2, mfdweight) / tot;
		else
			flow5 = 0;
		if (topo[i][j] > topo[iup[i]][jdown[j]])
			flow6 = pow((topo[i][j] - topo[iup[i]][jdown[j]]) * oneoversqrt2, mfdweight) / tot;
		else
			flow6 = 0;
		if (topo[i][j] > topo[idown[i]][jup[j]])
			flow7 = pow((topo[i][j] - topo[idown[i]][jup[j]]) * oneoversqrt2, mfdweight) / tot;
		else
			flow7 = 0;
		if (topo[i][j] > topo[idown[i]][jdown[j]])
			flow8 = pow((topo[i][j] - topo[idown[i]][jdown[j]]) * oneoversqrt2, mfdweight) / tot;
		else
			flow8 = 0;
		area[iup[i]][j] += area[i][j] * flow1;
		area[idown[i]][j] += area[i][j] * flow2;
		area[i][jup[j]] += area[i][j] * flow3;
		area[i][jdown[j]] += area[i][j] * flow4;
		area[iup[i]][jup[j]] += area[i][j] * flow5;
		area[iup[i]][jdown[j]] += area[i][j] * flow6;
		area[idown[i]][jup[j]] += area[i][j] * flow7;
		area[idown[i]][jdown[j]] += area[i][j] * flow8;
	}
}

void calculateslope()
{
	int i, j;

	i1 = imatrix(1, lattice_size_x, 1, lattice_size_y);
	jl = imatrix(1, lattice_size_x, 1, lattice_size_y);
	i2 = imatrix(1, lattice_size_x, 1, lattice_size_y);
	j2 = imatrix(1, lattice_size_x, 1, lattice_size_y);
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
		{
			i1[i][j] = -99;
			slopex = topo[iup[i]][j] - topo[idown[i]][j];
			slopey = topo[i][jup[j]] - topo[i][jdown[j]];
			slope[i][j] = 0.5 * sqrt(slopex * slopex + slopey * slopey) * oneoverdeltax;
			if (slope[i][j] < minslope)
				slope[i][j] = minslope;
			angle[i][j] = atan(slopey / slopex) + PI / 2;
			if (slopex > 0)
				angle[i][j] += PI;
			if (fabs(slopex) < small)
			{
				if (slopey > 0)
					angle[i][j] = 2 * PI;
				else
					angle[i][j] = PI;
			}
			if ((angle[i][j] >= 0) && (angle[i][j] <= PIover4))
			{
				i1[i][j] = iup[i];
				jl[i][j] = jdown[j];
				i2[i][j] = i;
				j2[i][j] = jdown[j];
			}
			else if ((angle[i][j] > PIover4) && (angle[i][j] <= 2 * PIover4))
			{
				i1[i][j] = iup[i];
				jl[i][j] = j;
				i2[i][j] = iup[i];
				j2[i][j] = jdown[j];
			}
			else if ((angle[i][j] > 2 * PIover4) && (angle[i][j] <= 3 * PIover4))
			{
				i1[i][j] = iup[i];
				jl[i][j] = jup[j];
				i2[i][j] = iup[i];
				j2[i][j] = j;
			}
			else if ((angle[i][j] > 3 * PIover4) && (angle[i][j] <= 4 * PIover4))
			{
				i1[i][j] = i;
				jl[i][j] = jup[j];
				i2[i][j] = iup[i];
				j2[i][j] = jup[j];
			}
			else if ((angle[i][j] > 4 * PIover4) && (angle[i][j] <= 5 * PIover4))
			{
				i1[i][j] = idown[i];
				jl[i][j] = jup[j];
				i2[i][j] = i;
				j2[i][j] = jup[j];
			}
			else if ((angle[i][j] > 5 * PIover4) && (angle[i][j] <= 6 * PIover4))
			{
				i1[i][j] = idown[i];
				jl[i][j] = j;
				i2[i][j] = idown[i];
				j2[i][j] = jup[j];
			}
			else if ((angle[i][j] > 6 * PIover4) && (angle[i][j] <= 7 * PIover4))
			{
				i1[i][j] = idown[i];
				jl[i][j] = jdown[j];
				i2[i][j] = idown[i];
				j2[i][j] = j;
			}
			else if ((angle[i][j] > 7 * PIover4) && (angle[i][j] <= 8 * PIover4))
			{
				i1[i][j] = i;
				jl[i][j] = jdown[j];
				i2[i][j] = idown[i];
				j2[i][j] = jdown[j];
			}
			if (i1[i][j] > 0)
				if ((topo[i][j] <= topo[i1[i][j]][jl[i][j]]) || (topo[i][j] <= topo[i2[i][j]][j2[i][j]]))
				{
					slope[i][j] = topo[i][j] - topo[iup[i]][j];
					angle[i][j] = 2 * PIover4;
					if (topo[i][j] - topo[idown[i]][j] > slope[i][j])
					{
						slope[i][j] = topo[i][j] - topo[idown[i]][j];
						angle[i][j] = 6 * PIover4;
					}
					if (topo[i][j] - topo[i][jup[j]] > slope[i][j])
					{
						slope[i][j] = topo[i][j] - topo[i][jup[j]];
						angle[i][j] = 4 * PIover4;
					}
					if (topo[i][j] - topo[i][jdown[j]] > slope[i][j])
					{
						slope[i][j] = topo[i][j] - topo[i][jdown[j]];
						angle[i][j] = 0;
					}
					if ((topo[i][j] - topo[iup[i]][jup[j]]) * oneoversqrt2 > slope[i][j])
					{
						slope[i][j] = (topo[i][j] - topo[iup[i]][jup[j]]) * oneoversqrt2;
						angle[i][j] = 3 * PIover4;
					}
					if ((topo[i][j] - topo[iup[i]][jdown[j]]) * oneoversqrt2 > slope[i][j])
					{
						slope[i][j] = (topo[i][j] - topo[iup[i]][jdown[j]]) * oneoversqrt2;
						angle[i][j] = PIover4;
					}
					if ((topo[i][j] - topo[idown[i]][jup[j]]) * oneoversqrt2 > slope[i][j])
					{
						slope[i][j] = (topo[i][j] - topo[idown[i]][jup[j]]) * oneoversqrt2;
						angle[i][j] = 5 * PIover4;
					}
					if ((topo[i][j] - topo[idown[i]][jdown[j]]) * oneoversqrt2 > slope[i][j])
					{
						slope[i][j] = (topo[i][j] - topo[idown[i]][jdown[j]]) * oneoversqrt2;
						angle[i][j] = 7 * PIover4;
					}
					slope[i][j] *= oneoverdeltax;
					if (slope[i][j] < minslope)
						slope[i][j] = minslope;
				}
		}
	free_imatrix(i1, 1, lattice_size_x, 1, lattice_size_y);
	free_imatrix(jl, 1, lattice_size_x, 1, lattice_size_y);
	free_imatrix(i2, 1, lattice_size_x, 1, lattice_size_y);
	free_imatrix(j2, 1, lattice_size_x, 1, lattice_size_y);
	if (smoothinglength > 1)
		smoothslope();
}

void mfdroutefordischarge(int i, int j)
{
	double fluxtot, discharge1, discharge2, discharge3, discharge4, discharge5, discharge6, discharge7, discharge8;

	if (topo[i][j] > topo[iup[i]][j])
		discharge1 = pow(topo[i][j] - topo[iup[i]][j], mfdweight);
	else
		discharge1 = 0;
	if (topo[i][j] > topo[idown[i]][j])
		discharge2 = pow(topo[i][j] - topo[idown[i]][j], mfdweight);
	else
		discharge2 = 0;
	if (topo[i][j] > topo[i][jup[j]])
		discharge3 = pow(topo[i][j] - topo[i][jup[j]], mfdweight);
	else
		discharge3 = 0;
	if (topo[i][j] > topo[i][jdown[j]])
		discharge4 = pow(topo[i][j] - topo[i][jdown[j]], mfdweight);
	else
		discharge4 = 0;
	if (topo[i][j] > topo[iup[i]][jup[j]])
		discharge5 = pow((topo[i][j] - topo[iup[i]][jup[j]]) * oneoversqrt2, mfdweight);
	else
		discharge5 = 0;
	if (topo[i][j] > topo[iup[i]][jdown[j]])
		discharge6 = pow((topo[i][j] - topo[iup[i]][jdown[j]]) * oneoversqrt2, mfdweight);
	else
		discharge6 = 0;
	if (topo[i][j] > topo[idown[i]][jup[j]])
		discharge7 = pow((topo[i][j] - topo[idown[i]][jup[j]]) * oneoversqrt2, mfdweight);
	else
		discharge7 = 0;
	if (topo[i][j] > topo[idown[i]][jdown[j]])
		discharge8 = pow((topo[i][j] - topo[idown[i]][jdown[j]]) * oneoversqrt2, mfdweight);
	else
		discharge8 = 0;
	fluxtot = discharge1 + discharge2 + discharge3 + discharge4 + discharge5 + discharge6 + discharge7 + discharge8;
	if (fluxtot > 0)
	{
		discharge[iup[i]][j] += discharge[i][j] * discharge1 / fluxtot;
		discharge[idown[i]][j] += discharge[i][j] * discharge2 / fluxtot;
		discharge[i][jup[j]] += discharge[i][j] * discharge3 / fluxtot;
		discharge[i][jdown[j]] += discharge[i][j] * discharge4 / fluxtot;
		discharge[iup[i]][jup[j]] += discharge[i][j] * discharge5 / fluxtot;
		discharge[iup[i]][jdown[j]] += discharge[i][j] * discharge6 / fluxtot;
		discharge[idown[i]][jup[j]] += discharge[i][j] * discharge7 / fluxtot;
		discharge[idown[i]][jdown[j]] += discharge[i][j] * discharge8 / fluxtot;
	}
}

void initialguessforrouting()
{
	int i, j;

	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			topoorig[i][j] = topo[i][j];
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
		{
			if (mask[i][j] == 1)
				discharge[i][j] = deltax * deltax * rain[i][j] * b / (1000 * 3600);
			else
				discharge[i][j] = 0;
			topovec[(j - 1) * lattice_size_x + i] = topo[i][j];
		}
	calculateslope();
	indexx(lattice_size_x * lattice_size_y, topovec, topovecind);
	t = lattice_size_x * lattice_size_y + 1;
	while (t > 1)
	{
		t--;
		i = (topovecind[t]) % lattice_size_x;
		if (i == 0)
			i = lattice_size_x;
		j = (topovecind[t]) / lattice_size_x + 1;
		if (i == lattice_size_x)
			j--;
		if (mask[i][j] == 1)
			mfdroutefordischarge(i, j);
	}
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			if (mask[i][j] == 1)
			{
				depth[i][j] = pow(discharge[i][j] * manningsn / (deltax * sqrt(slope[i][j])), 0.6);
				topo[i][j] += depth[i][j];
			}
			else
				depth[i][j] = 0;
}

void calculatedischargefluxes(int i, int j)
{
	double fluxtot, averagedepth, slope1, slope2, slope3, slope4, slope5, slope6, slope7, slope8, discharge1, discharge2, discharge3, discharge4, discharge5, discharge6, discharge7, discharge8;

	slope1 = topo[i][j] - topo[iup[i]][j];
	averagedepth = weightfactor * depth[i][j] + oneminusweightfactor * depth[iup[i]][j];
	if ((topo[i][j] > topo[iup[i]][j]) && (averagedepth > 0))
		discharge1 = pow(slope1, mfdweight) * pow(averagedepth, tenthirdstimesmfdweight) / pow(manningsn, twicemfdweight);
	else
		discharge1 = 0;
	slope2 = topo[i][j] - topo[idown[i]][j];
	averagedepth = weightfactor * depth[i][j] + oneminusweightfactor * depth[idown[i]][j];
	if ((topo[i][j] > topo[idown[i]][j]) && (averagedepth > 0))
		discharge2 = pow(slope2, mfdweight) * pow(averagedepth, tenthirdstimesmfdweight) / pow(manningsn, twicemfdweight);
	else
		discharge2 = 0;
	slope3 = topo[i][j] - topo[i][jup[j]];
	averagedepth = weightfactor * depth[i][j] + oneminusweightfactor * depth[i][jup[j]];
	if ((topo[i][j] > topo[i][jup[j]]) && (averagedepth > 0))
		discharge3 = pow(slope3, mfdweight) * pow(averagedepth, tenthirdstimesmfdweight) / pow(manningsn, twicemfdweight);
	else
		discharge3 = 0;
	slope4 = topo[i][j] - topo[i][jdown[j]];
	averagedepth = weightfactor * depth[i][j] + oneminusweightfactor * depth[i][jdown[j]];
	if ((topo[i][j] > topo[i][jdown[j]]) && (averagedepth > 0))
		discharge4 = pow(slope4, mfdweight) * pow(averagedepth, tenthirdstimesmfdweight) / pow(manningsn, twicemfdweight);
	else
		discharge4 = 0;
	slope5 = (topo[i][j] - topo[iup[i]][jup[j]]) * oneoversqrt2;
	averagedepth = weightfactor * depth[i][j] + oneminusweightfactor * depth[iup[i]][jup[j]];
	if ((topo[i][j] > topo[iup[i]][jup[j]]) && (averagedepth > 0))
		discharge5 = pow(slope5, mfdweight) * pow(averagedepth, tenthirdstimesmfdweight) / pow(manningsn, twicemfdweight);
	else
		discharge5 = 0;
	slope6 = (topo[i][j] - topo[idown[i]][jup[j]]) * oneoversqrt2;
	averagedepth = weightfactor * depth[i][j] + oneminusweightfactor * depth[idown[i]][jup[j]];
	if ((topo[i][j] > topo[idown[i]][jup[j]]) && (averagedepth > 0))
		discharge6 = pow(slope6, mfdweight) * pow(averagedepth, tenthirdstimesmfdweight) / pow(manningsn, twicemfdweight);
	else
		discharge6 = 0;
	slope7 = (topo[i][j] - topo[iup[i]][jdown[j]]) * oneoversqrt2;
	averagedepth = weightfactor * depth[i][j] + oneminusweightfactor * depth[iup[i]][jdown[j]];
	if ((topo[i][j] > topo[iup[i]][jdown[j]]) && (averagedepth > 0))
		discharge7 = pow(slope7, mfdweight) * pow(averagedepth, tenthirdstimesmfdweight) / pow(manningsn, twicemfdweight);
	else
		discharge7 = 0;
	slope8 = (topo[i][j] - topo[idown[i]][jdown[j]]) * oneoversqrt2;
	averagedepth = weightfactor * depth[i][j] + oneminusweightfactor * depth[idown[i]][jdown[j]];
	if ((topo[i][j] > topo[idown[i]][jdown[j]]) && (averagedepth > 0))
		discharge8 = pow(slope8, mfdweight) * pow(averagedepth, tenthirdstimesmfdweight) / pow(manningsn, twicemfdweight);
	else
		discharge8 = 0;
	fluxtot = discharge1 + discharge2 + discharge3 + discharge4 + discharge5 + discharge6 + discharge7 + discharge8;
	if (fluxtot > 0)
	{
		discharge[iup[i]][j] += discharge1 * discharge[i][j] / fluxtot;
		discharge[idown[i]][j] += discharge2 * discharge[i][j] / fluxtot;
		discharge[i][jup[j]] += discharge3 * discharge[i][j] / fluxtot;
		discharge[i][jdown[j]] += discharge4 * discharge[i][j] / fluxtot;
		discharge[iup[i]][jup[j]] += discharge5 * discharge[i][j] / fluxtot;
		discharge[idown[i]][jup[j]] += discharge6 * discharge[i][j] / fluxtot;
		discharge[iup[i]][jdown[j]] += discharge7 * discharge[i][j] / fluxtot;
		discharge[idown[i]][jdown[j]] += discharge8 * discharge[i][j] / fluxtot;
	}
}

void routing()
{
	int i, j, k, k2;

	priority_flood_epsilon();
	initialguessforrouting();
	priority_flood_epsilon();
	k2 = 0;
	while (k2 < numberofsweeps)
	{
		k = 0;
		k2++;
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				depthold[i][j] = depth[i][j];
		while (k <= numberofslices)
		{
			k++;
			for (j = 1; j <= lattice_size_y; j++)
				for (i = 1; i <= lattice_size_x; i++)
					discharge[i][j] = rain[i][j] * deltax * deltax / (1000 * 3600);
			calculateslope();
			indexx(lattice_size_x * lattice_size_y, topovec, topovecind);
			t = lattice_size_x * lattice_size_y + 1;
			while (t > 1)
			{
				t--;
				i = (topovecind[t]) % lattice_size_x;
				if (i == 0)
					i = lattice_size_x;
				j = (topovecind[t]) / lattice_size_x + 1;
				if (i == lattice_size_x)
					j--;
				if ((mask[i][j] == 1) && (slope[i][j] > minslope))
					calculatedischargefluxes(i, j);
			}
			for (j = 1; j <= lattice_size_y; j++)
				for (i = 1; i <= lattice_size_x; i++)
					if (mask[i][j] == 1)
					{
						area[i][j] = discharge[i][j] * 1000 * 3600 / rain[i][j];
						discharge[i][j] = b * rain[i][j] / (1000 * 3600) * pow(area[i][j], c);
						depth[i][j] = pow(discharge[i][j] * manningsn / (deltax * sqrt(slope[i][j])), 0.6);
						topo[i][j] += (topoorig[i][j] + depth[i][j] - topo[i][j]) / numberofslices;
					}
			priority_flood_epsilon();
		}
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				depth[i][j] = topo[i][j] - topoorig[i][j];
	}
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			discharge[i][j] = pow(depth[i][j], fivethirds) * sqrt(slope[i][j]) * deltax / manningsn;
}

void calculatedischarge()
{
	int i, j;

	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			topovec[(j - 1) * lattice_size_x + i] = topo[i][j];
	indexx(lattice_size_x * lattice_size_y, topovec, topovecind);
	t = lattice_size_x * lattice_size_y + 1;
	if ((flagforroutingmethod == 0) || (flagforroutingmethod == 2))
	{
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				area[i][j] = rain[i][j] * deltax * deltax / (1000 * 3600);
		while (t > 1)
		{
			t--;
			i = (topovecind[t]) % lattice_size_x;
			if (i == 0)
				i = lattice_size_x;
			j = (topovecind[t]) / lattice_size_x + 1;
			if (i == lattice_size_x)
				j--;
			if (mask[i][j] == 1)
			{
				if (flagforroutingmethod == 0)
					mfdflowrouteorig(i, j);
				else
					dinfflowrouteorig(i, j);
				area[i][j] *= 1000 * 3600 / rain[i][j];
				discharge[i][j] = b * rain[i][j] / (1000 * 3600) * pow(area[i][j], c);
				depth[i][j] = pow(discharge[i][j] * manningsn / (deltax * sqrt(slope[i][j])), 0.6);
			}
			else
			{
				discharge[i][j] = 0;
				depth[i][j] = 0;
			}
		}
	}
	else
	{
		oneminusweightfactor = 1 - weightfactor;
		routing();
	}
}

void setupgrids()
{
	mask = imatrix(1, lattice_size_x, 1, lattice_size_y);
	topo = matrix(1, lattice_size_x, 1, lattice_size_y);
	slope = matrix(1, lattice_size_x, 1, lattice_size_y);
	rain = matrix(1, lattice_size_x, 1, lattice_size_y);
	area = matrix(1, lattice_size_x, 1, lattice_size_y);
	discharge = matrix(1, lattice_size_x, 1, lattice_size_y);
	depth = matrix(1, lattice_size_x, 1, lattice_size_y);
	inciseddepth = matrix(1, lattice_size_x, 1, lattice_size_y);
	eroded = matrix(1, lattice_size_x, 1, lattice_size_y);
	tau = matrix(1, lattice_size_x, 1, lattice_size_y);
	maxtau = matrix(1, lattice_size_x, 1, lattice_size_y);
	angle = matrix(1, lattice_size_x, 1, lattice_size_y);
	slopefactor = matrix(1, lattice_size_x, 1, lattice_size_y);
	sinofslope = matrix(1, lattice_size_x, 1, lattice_size_y);
	cosofslopeterm = matrix(1, lattice_size_x, 1, lattice_size_y);
	taucarmor = matrix(1, lattice_size_x, 1, lattice_size_y);
	taucsoilandveg = matrix(1, lattice_size_x, 1, lattice_size_y);
	d50 = matrix(1, lattice_size_x, 1, lattice_size_y);
	rockcover = matrix(1, lattice_size_x, 1, lattice_size_y);
	rockthickness = matrix(1, lattice_size_x, 1, lattice_size_y);
	f1 = matrix(1, lattice_size_x, 1, lattice_size_y);
	f2 = matrix(1, lattice_size_x, 1, lattice_size_y);
	topoorig = matrix(1, lattice_size_x, 1, lattice_size_y);
	depthold = matrix(1, lattice_size_x, 1, lattice_size_y);
	topovec = vector(1, lattice_size_x * lattice_size_y);
	topovecind = lvector(1, lattice_size_x * lattice_size_y);
}

void freememory()
{
	free_imatrix(mask, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(topo, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(slope, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(rain, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(area, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(depth, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(inciseddepth, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(discharge, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(eroded, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(tau, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(maxtau, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(angle, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(slopefactor, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(sinofslope, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(cosofslopeterm, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(taucarmor, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(taucsoilandveg, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(d50, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(rockcover, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(rockthickness, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(f1, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(f2, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(topoorig, 1, lattice_size_x, 1, lattice_size_y);
	free_matrix(depthold, 1, lattice_size_x, 1, lattice_size_y);
	free_vector(topovec, 1, lattice_size_x * lattice_size_y);
	free_lvector(topovecind, 1, lattice_size_x * lattice_size_y);
}

int main()
{
	FILE *fp1, *fp2, *fp3, *fp4, *fp5, *fp6, *fp7;
	int i, j, m, n;
	char temp[120];

	fp1 = fopen("./input.txt", "r");
	fp2 = fopen("./topo.txt", "r");
	fp3 = fopen("./f1.txt", "w");
	fp4 = fopen("./f2.txt", "w");
	fp5 = fopen("./rills.ppm", "w");
	fp6 = fopen("./tau.txt", "w");
	fscanf(fp1, "%d %s\n", &flagformode, temp);
	fscanf(fp1, "%d %s\n", &flagforroutingmethod, temp);
	fscanf(fp1, "%d %s\n", &flagforshearstressequation, temp);
	fscanf(fp1, "%d %s\n", &flagformask, temp);
	fscanf(fp1, "%d %s\n", &flagfortaucsoilandveg, temp);
	fscanf(fp1, "%d %s\n", &flagford50, temp);
	fscanf(fp1, "%d %s\n", &flagforrockthickness, temp);
	fscanf(fp1, "%d %s\n", &flagforrockcover, temp);
	fscanf(fp1, "%lf %s\n", &fillincrement, temp);
	fscanf(fp1, "%lf %s\n", &minslope, temp);
	fscanf(fp1, "%d %s\n", &expansion, temp);
	fscanf(fp1, "%lf %s\n", &yellowthreshold, temp);
	fscanf(fp1, "%d %s\n", &lattice_size_x, temp);
	fscanf(fp1, "%d %s\n", &lattice_size_y, temp);
	fscanf(fp1, "%lf %s\n", &deltax, temp);
	fscanf(fp1, "%lf %s\n", &nodatavalue, temp);
	fscanf(fp1, "%d %s\n", &smoothinglength, temp);
	fscanf(fp1, "%lf %s\n", &manningsn, temp);
	fscanf(fp1, "%lf %s\n", &weightfactor, temp);
	fscanf(fp1, "%d %s\n", &numberofslices, temp);
	fscanf(fp1, "%d %s\n", &numberofsweeps, temp);
	fscanf(fp1, "%lf %s\n", &rainfixed, temp);
	fscanf(fp1, "%lf %s\n", &taucsoilandvegfixed, temp);
	fscanf(fp1, "%lf %s\n", &d50fixed, temp);
	fscanf(fp1, "%lf %s\n", &rockthicknessfixed, temp);
	fscanf(fp1, "%lf %s\n", &rockcoverfixed, temp);
	fscanf(fp1, "%lf %s\n", &tanangleofinternalfriction, temp);
	fscanf(fp1, "%lf %s\n", &b, temp);
	fscanf(fp1, "%lf %s\n", &c, temp);
	fscanf(fp1, "%lf %s\n", &rillwidthcoefficient, temp);
	fscanf(fp1, "%lf %s\n", &rillwidthexponent, temp);
	fclose(fp1);
	oneoverdeltax = 1. / deltax;
	setupgridneighbors();
	setupgrids();
	if (flagformask == 0)
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				mask[i][j] = 1;
	else
	{
		fp7 = fopen("./mask.txt", "r");
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
			{
				fscanf(fp7, "%d", &mask[i][j]);
				if (mask[i][j] > 0)
					mask[i][j] = 1;
			}
		fclose(fp7);
	}
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
		{
			fscanf(fp2, "%lf", &topo[i][j]);
			if (topo[i][j] <= nodatavalue)
				mask[i][j] = 0;
		}
	priority_flood_epsilon();
	calculateslope();
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
		{
			cosofslopeterm[i][j] = sqrt(9.81 * cos(atan(slope[i][j])));
			sinofslope[i][j] = sin(atan(slope[i][j]));
			slopefactor[i][j] = sin(atan(slope[i][j])) / (cos(atan(slope[i][j])) * tanangleofinternalfriction - sin(atan(slope[i][j])));
		}
	if (flagfortaucsoilandveg == 0)
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				taucsoilandveg[i][j] = taucsoilandvegfixed;
	else
	{
		fp7 = fopen("./taucsoilandveg.txt", "r");
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				fscanf(fp7, "%lf", &taucsoilandveg[i][j]);
		fclose(fp7);
	}
	if (flagford50 == 0)
	{
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				d50[i][j] = d50fixed;
	}
	else
	{
		fp7 = fopen("./d50.txt", "r");
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				fscanf(fp7, "%lf", &d50[i][j]);
		fclose(fp7);
	}
	if (flagforrockthickness == 0)
	{
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				rockthickness[i][j] = rockthicknessfixed;
	}
	else
	{
		fp7 = fopen("./rockthickness.txt", "r");
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				fscanf(fp7, "%lf", &rockthickness[i][j]);
		fclose(fp7);
	}
	if (flagforrockcover == 0)
	{
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				rockcover[i][j] = rockcoverfixed;
	}
	else
	{
		fp7 = fopen("./rockcover.txt", "r");
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				fscanf(fp7, "%lf", &rockcover[i][j]);
		fclose(fp7);
	}
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			if (mask[i][j] == 1)
			{
				if (flagforshearstressequation == 0)
					taucarmor[i][j] = 9810 * sinofslope[i][j] * pow(1.9 * pow(slope[i][j], -1.15) * pow(d50[i][j], 2.13) / cosofslopeterm[i][j], 0.666667);
				else
					taucarmor[i][j] = 9810 * sinofslope[i][j] * pow(1.3 * pow(slopefactor[i][j], -0.86) * pow(d50[i][j], 1.68) / cosofslopeterm[i][j], 0.666667);
				if ((rockcover[i][j] < 0.99) && (rockcover[i][j] > 0.3))
					taucarmor[i][j] *= exp(-3.6) / exp(-4 * (rockcover[i][j] - 0.1));
				if (taucarmor[i][j] < taucsoilandveg[i][j])
					taucarmor[i][j] = taucsoilandveg[i][j];
			}
	if (flagformode == 0)
	{
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				rain[i][j] = rainfixed;
		calculatedischarge();
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
			{
				rillwidth = rillwidthcoefficient * pow(discharge[i][j], rillwidthexponent);
				if (rillwidth > deltax)
					rillwidth = deltax;
				maxtau[i][j] = 9810 * sinofslope[i][j] * pow(discharge[i][j] / (rillwidth * cosofslopeterm[i][j]), 0.666667);
				if (mask[i][j] > 0)
					depth[i][j] = pow(discharge[i][j] * manningsn / (deltax * sqrt(slope[i][j])), 0.6);
				else
					depth[i][j] = 0;
				if (discharge[i][j] > 0)
					f1[i][j] = taucarmor[i][j] / maxtau[i][j];
				else
					f1[i][j] = large;
				if (depth[i][j] > 0)
					f2[i][j] = rockthickness[i][j] / depth[i][j];
				else
					f2[i][j] = large;
			}
	}
	else
	{
		fp1 = fopen("./variableinput.txt", "r");
		fscanf(fp1, "%lf %s", &rillerodibilitycoefficient, temp);
		fscanf(fp1, "%lf %s", &bulkdensity, temp);
		fscanf(fp1, "%lf %s", &timestep, temp);
		fscanf(fp1, "%d %s", &numberofraingages, temp);
		fscanf(fp1, "%lf %lf", &ulx, &uly);
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
			{
				maxtau[i][j] = 0;
				inciseddepth[i][j] = 0;
				eroded[i][j] = 0;
				if (mask[i][j] == 1)
				{
					f1[i][j] = 2;
					f2[i][j] = 2;
				}
				else
				{
					f1[i][j] = 0;
					f2[i][j] = 0;
				}
			}
		fp7 = fopen("./inciseddepth.txt", "w");
		raingagex = vector(1, numberofraingages);
		raingagey = vector(1, numberofraingages);
		closestgage = imatrix(1, lattice_size_x, 1, lattice_size_y);
		nextclosestgage = imatrix(1, lattice_size_x, 1, lattice_size_y);
		distancetoclosestgage = matrix(1, lattice_size_x, 1, lattice_size_y);
		distancetonextclosestgage = matrix(1, lattice_size_x, 1, lattice_size_y);
		for (m = 1; m <= numberofraingages; m++)
			fscanf(fp1, "%lf %lf", &raingagex[m], &raingagey[m]);
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
			{
				distancetoclosestgage[i][j] = large;
				f1[i][j] = large;
				f2[i][j] = large;
				for (m = 1; m <= numberofraingages; m++)
				{
					ic = oneoverdeltax * (raingagex[m] - ulx);
					jc = oneoverdeltax * (uly - raingagey[m]);
					dist = sqrt((i - ic - 1) * (i - ic - 1) + (j - jc - 1) * (j - jc - 1));
					if (dist < distancetoclosestgage[i][j])
					{
						distancetoclosestgage[i][j] = dist;
						closestgage[i][j] = m;
					}
				}
			}
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
			{
				distancetonextclosestgage[i][j] = large;
				for (m = 1; m <= numberofraingages; m++)
				{
					ic = oneoverdeltax * (raingagex[m] - ulx);
					jc = oneoverdeltax * (uly - raingagey[m]);
					dist = sqrt((i - ic - 1) * (i - ic - 1) + (j - jc - 1) * (j - jc - 1));
					if ((dist < distancetonextclosestgage[i][j]) && (dist > distancetoclosestgage[i][j]))
					{
						distancetonextclosestgage[i][j] = dist;
						nextclosestgage[i][j] = m;
					}
				}
			}
		fscanf(fp1, "%d", &numberofraindata);
		rainvalues = vector(1, numberofraindata);
		for (n = 1; n <= numberofraindata; n++)
		{
			printf("processing time interval %d of %d\n", n, numberofraindata);
			for (m = 1; m <= numberofraingages; m++)
				fscanf(fp1, "%lf", &rainvalues[m]);
			for (j = 1; j <= lattice_size_y; j++)
				for (i = 1; i <= lattice_size_x; i++)
					rain[i][j] = (rainvalues[closestgage[i][j]] * distancetonextclosestgage[i][j] + rainvalues[nextclosestgage[i][j]] * distancetoclosestgage[i][j]) / (distancetoclosestgage[i][j] + distancetonextclosestgage[i][j]);
			calculatedischarge();
			for (j = 1; j <= lattice_size_y; j++)
				for (i = 1; i <= lattice_size_x; i++)
				{
					rillwidth = rillwidthcoefficient * pow(discharge[i][j], rillwidthexponent);
					if (rillwidth > deltax)
						rillwidth = deltax;
					tau[i][j] = 9810 * sinofslope[i][j] * pow(discharge[i][j] / (rillwidth * cosofslopeterm[i][j]), 0.666667);
					if (tau[i][j] > maxtau[i][j])
						maxtau[i][j] = tau[i][j];
					f1l = taucarmor[i][j] / tau[i][j];
					if (f1[i][j] > f1l)
						f1[i][j] = f1l;
					if (depth[i][j] > 0)
						f2l = rockthickness[i][j] / depth[i][j];
					else
						f2l = large;
					if (f2[i][j] > f2l)
						f2[i][j] = f2l;
					if ((slope[i][j] < tanangleofinternalfriction) && (f1l < 1))
					{
						excessshearstress = tau[i][j] - taucarmor[i][j];
						incisionincrement = rillerodibilitycoefficient * excessshearstress * 60 * timestep / bulkdensity;
						inciseddepth[i][j] += incisionincrement;
						eroded[i][j] += rillwidth / deltax * incisionincrement;
					}
				}
		}
		sumarea = 0;
		sumerosion = 0;
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
			{
				if (mask[i][j] > 0)
					sumarea++;
				if (eroded[i][j] > 0)
					sumerosion += eroded[i][j];
			}
		printf("average sediment yield %f t/ha\n", sumerosion * bulkdensity / 1000 * 10000 / sumarea); // conversions result in metric tons per ha
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				if (mask[i][j] == 1)
					fprintf(fp7, "%f\n", inciseddepth[i][j]);
				else
					fprintf(fp7, "0.0\n");
		fclose(fp1);
		fclose(fp7);
	}
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
		{
			if (mask[i][j] == 1)
			{
				if ((f1[i][j] < 2) && (f1[i][j] > -large) && (f1[i][j] < large))
					fprintf(fp3, "%f\n", f1[i][j]);
				else
				{
					if (f1[i][j] >= 2)
						fprintf(fp3, "2.0\n");
					else
						fprintf(fp3, "0.0\n");
				}
			}
			else
				fprintf(fp3, "0.0\n");
			if (mask[i][j] == 1)
			{
				f2[i][j] = rockthickness[i][j] / depth[i][j];
				if ((f2[i][j] < 2) && (f2[i][j] > -large) && (f2[i][j] < large))
					fprintf(fp4, "%f\n", f2[i][j]);
				else
				{
					if (f2[i][j] > 2)
						fprintf(fp4, "2.0\n");
					else
						fprintf(fp4, "0.0\n");
				}
			}
			else
				fprintf(fp4, "0.0\n");
			if (mask[i][j] == 1)
				fprintf(fp6, "%f\n", maxtau[i][j]);
			else
				fprintf(fp6, "0.0\n");
		}
	fprintf(fp5, "P3\n%d %d\n255\n", lattice_size_x, lattice_size_y);
	for (m = 1; m <= expansion; m++)
	{
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				f2[i][j] = f1[i][j];
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				if ((f2[iup[i]][j] <= 1) || (f2[idown[i]][j] <= 1) || (f2[i][jup[j]] <= 1) || (f2[i][jdown[j]] <= 1))
					f1[i][j] = 0.99;
	}
	for (m = 1; m <= expansion; m++)
	{
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				f2[i][j] = f1[i][j];
		for (j = 1; j <= lattice_size_y; j++)
			for (i = 1; i <= lattice_size_x; i++)
				if (((f2[iup[i]][j] <= yellowthreshold) && (f2[i][j] > 1)) || ((f2[idown[i]][j] <= yellowthreshold) && (f2[idown[i]][j] > 1)) || ((f2[i][jup[j]] <= yellowthreshold) && (f2[i][jup[j]] > 1)) || ((f2[i][jdown[j]] <= yellowthreshold) && (f2[i][jdown[j]] > 1)))
					f1[i][j] = yellowthreshold - 0.01;
	}
	for (j = 1; j <= lattice_size_y; j++)
		for (i = 1; i <= lattice_size_x; i++)
			if (mask[i][j] == 0)
				fprintf(fp5, "0 0 0\n");
			else
			{
				if (f1[i][j] < 1)
					fprintf(fp5, "255 0 0\n");
				else if (f1[i][j] < yellowthreshold)
					fprintf(fp5, "255 255 0\n");
				else
					fprintf(fp5, "255 255 255\n");
			}
	fclose(fp2);
	fclose(fp3);
	fclose(fp4);
	fclose(fp5);
	fclose(fp6);
	freememory();
}