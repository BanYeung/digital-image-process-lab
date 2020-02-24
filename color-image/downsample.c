
void downsample(char *src, char *dst, int src_cols, int dst_rows, int dst_cols) {
	
	int i,k;
	char *ap_2, *ap_1, *p, *bp_1, *bp_2;
	unsigned int part_36, part_24, part_16, part_4, part_1, part_6;
	
	//ignore the edge of dst
for(i = 1; i < dst_rows - 1; i ++)
	for(k = 1; k < dst_cols - 1; k ++) {
		/*
			_ _ ap_2 _ _
			_ _ ap_1 _ _
			_ _ p	 _ _
			_ _ bp_1 _ _
			_ _ bp_2 _ _
		*/
		p = src + (src_cols * 2*i) + 2*k;	//the address of kernel's center
		ap_1 = p - src_cols;		
		ap_2 = p - 2 * src_cols;
		bp_1 = p + src_cols;
		bp_2 = p + 2 * src_cols;
		
		//36
		part_36 = 36*(*p);
		
		//24
		part_24 = 24*( *ap_1 + *bp_1 + *(p-1) + *(p+1) );
		
		//16
		part_16 = ( *(ap_1-1) + *(ap_1+1) + *(bp_1-1) + *(bp_1+1) ) << 4;
		
		//6
		part_6 = ( *(ap_2) + *(p-2) + *(bp_2) + *(p+2) ) * 6;
		
		//4
		part_4 = ( *(ap_2-1) + *(ap_2+1) + *(bp_2-1) + *(bp_2+1) +
				   *(ap_1-2) + *(ap_1+2) + *(bp_1-2) + *(bp_1+2) ) << 2;
				   
		//1
		part_1 = *(ap_2-2) + *(ap_2+2) + *(bp_2+2) + *(bp_2-2);
		
		*(dst+(dst_cols*i + k)) = (part_24 + part_16 + part_6 + part_4 + part_36 + part_1) >> 8; 			
	}
}