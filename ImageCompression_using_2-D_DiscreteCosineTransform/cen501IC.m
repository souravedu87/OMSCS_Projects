%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 
%   Topic: 2-D Discrete Cosine Transform Image Compression
%   CEN 501 - Fall 2014
%   Arizona State University
%   by: SOURAV SAMANTA
%   ASU Id: 1207860455
%   Email: ssamant4@asu.edu
%   
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function cen501IC()
clc
close all

%Input the 512 X 512 .RAW image
rawImage = fopen('lena.raw','r');
orgImage = fread(rawImage);
fclose(rawImage);
orgImage = reshape(orgImage,512,512);
orgImage = orgImage.';

%Perform Level Translation (Pixel = Pixel - 128) 
lvlTransImage = orgImage - 128;

%Divide the Image into 8 X 8 blocks and apply custom 2-D DCT 'fDct2'
%function to obtain DCT Coefficient Matrix
fun = @(block_struct) fDct2(block_struct.data);
dctCoeffMat = blockproc(lvlTransImage,[8 8],fun);

%Mask-1 (Setting lower one-quarter of the Mask to zero)
mask1 = [1 1 1 1 1 1 1 1
         1 1 1 1 1 1 1 1
         1 1 1 1 1 1 1 1
         1 1 1 1 1 1 1 0
         1 1 1 1 1 1 0 0
         1 1 1 1 0 0 0 0
         1 1 1 1 0 0 0 0
         1 1 1 0 0 0 0 0];

%Mask-2 (Setting lower one-half of the Mask to zero)
mask2 = [1 1 1 1 1 1 1 1
         1 1 1 1 1 1 1 0
         1 1 1 1 1 0 0 0
         1 1 1 1 0 0 0 0
         1 1 1 0 0 0 0 0
         1 1 0 0 0 0 0 0
         1 1 0 0 0 0 0 0
         1 0 0 0 0 0 0 0];

%Mask-3 (Setting three-fourth of the Mask to zero)
mask3 = [1 1 1 1 1 0 0 0
         1 1 1 1 0 0 0 0
         1 1 1 0 0 0 0 0
         1 1 0 0 0 0 0 0
         1 0 0 0 0 0 0 0
         1 0 0 0 0 0 0 0
         0 0 0 0 0 0 0 0
         0 0 0 0 0 0 0 0];

%Perfom Masking using 'fMask' function
maskedImage1 = fMask(dctCoeffMat,mask1);
maskedImage2 = fMask(dctCoeffMat,mask2);
maskedImage3 = fMask(dctCoeffMat,mask3);

%Compress Masked Images using 'fCompress' function
[comImage1,mean8x8a,std8x8a,step8x8a] = fCompress(maskedImage1);
[comImage2,mean8x8b,std8x8b,step8x8b] = fCompress(maskedImage2);
[comImage3,mean8x8c,std8x8c,step8x8c] = fCompress(maskedImage3);

%Decompress Images using 'fDecompress' function
recImage1 = fDecompress(comImage1,mean8x8a,std8x8a,step8x8a);
recImage2 = fDecompress(comImage2,mean8x8b,std8x8b,step8x8b);
recImage3 = fDecompress(comImage3,mean8x8c,std8x8c,step8x8c);

%Calculate the Magnitude Spectrum of Images by 2-D DFT using 'fDft2'
%function
dft2OrgImage = fDft2(orgImage);
dft2RecImage1 = fDft2(recImage1);
dft2RecImage2 = fDft2(recImage2);
dft2RecImage3 = fDft2(recImage3);

%Calculate Total no. of bits to code the Image & Average number of
%bits/pixel
[totBits1,avgBitsPerPixel1] = fCalTotAvgBits(comImage1);
[totBits2,avgBitsPerPixel2] = fCalTotAvgBits(comImage2);
[totBits3,avgBitsPerPixel3] = fCalTotAvgBits(comImage3);

%Calculate the PSNR of the Images
psnrVal1 = fCalPsnr(recImage1,orgImage);
psnrVal2 = fCalPsnr(recImage2,orgImage);
psnrVal3 = fCalPsnr(recImage3,orgImage);

%Display Data
set(gcf,'Position',get(0,'Screensize')); 

subplot(2,4,1);
subimage(mat2gray(orgImage));
t1 = title({'Original Image';['Total no. of Bits = ',num2str(512*512*8)];['Average no. of bits/pixel = ',num2str(8)]});
set(t1,'FontSize',10);
axis off;
subplot(2,4,2);
subimage(mat2gray(recImage1));
t2 = title({'Reconstructed Image using One-Quarter Zero mask';['PSNR = ',num2str(psnrVal1),' dB & Total no. of Bits = ',num2str(totBits1)];['Average no. of bits/pixel = ',num2str(avgBitsPerPixel1)]});
set(t2,'FontSize',9);
axis off;
subplot(2,4,3);
subimage(mat2gray(recImage2));
t3 = title({'Reconstructed Image using Half Zero mask';['PSNR = ',num2str(psnrVal2),' dB & Total no. of Bits = ',num2str(totBits2)];['Average no. of bits/pixel = ',num2str(avgBitsPerPixel2)]});
set(t3,'FontSize',9);
axis off;
subplot(2,4,4);
subimage(mat2gray(recImage3));
t4 = title({'Reconstructed Image using Three-Quarter Zero mask';['PSNR = ',num2str(psnrVal3),' dB & Total no. of Bits = ',num2str(totBits3)];['Average no. of bits/pixel = ',num2str(avgBitsPerPixel3)]});
set(t4,'FontSize',9);
axis off;
subplot(2,4,5);
imagesc(dft2OrgImage);
colormap(gray);
title({'Magnitude Spectrum of';'Original Image'});
subplot(2,4,6);
imagesc(dft2RecImage1);
colormap(gray);
title({'Magnitude Spectrum of Reconstructed Image';'using One-Quarter Zero mask'});
subplot(2,4,7);
imagesc(dft2RecImage2);
colormap(gray);
title({'Magnitude Spectrum of Reconstructed Image';'using Half Zero mask'});
subplot(2,4,8);
imagesc(dft2RecImage3);
colormap(gray);
title({'Magnitude Spectrum of Reconstructed Image';'using Three-Quarter Zero mask'});


end

%Function for Masking
function Y = fMask(X,mask)
    
    fun = @(block_struct) block_struct.data .* mask;
    Y = blockproc(X,[8 8],fun);

end


%Function to Compress an Image
function [Y,mean8x8,std8x8,step8x8] = fCompress(X)
    
    %Calculate Mean, Standard Deviation & Step-size
    [mean8x8,std8x8,step8x8] = fcalMeanSdStepsize(X);
    
    %Normalize & Quantize
    fun = @(block_struct) fNormQuantize(block_struct.data,mean8x8,std8x8,step8x8);
    Y = blockproc(X,[8 8],fun);
    
end


%Function to Decompress an Image
function Y = fDecompress(X,mean8x8,std8x8,step8x8)

    %De-normalize & De-quantize
    fun1 = @(block_struct) ((block_struct.data .* std8x8 .* step8x8) + mean8x8);
    temp1Y = blockproc(X,[8 8],fun1);
    
    %Perform 2-D Inverse DCT using custom 'fIDct2' function
    fun2 = @(block_struct) fIDct2(block_struct.data);
    temp2Y = blockproc(temp1Y,[8 8],fun2);

    %Level Translation + 128
    Y = temp2Y + 128;
    
end

%2-D DCT function
function Y = fDct2(X)
    
    %Determine the dimensions of the Image
    [M,N] = size(X);
    Y = zeros(size(X));
    
    for p = 0:M-1
        if (p == 0)
            Ap = 1/sqrt(M);
        else
            Ap = sqrt(2/M);
        end
        for q = 0:N-1
            sum = 0;
            if (q == 0)
                Aq = 1/sqrt(N);
            else
                Aq = sqrt(2/N);
            end
            for m = 1:M
                for n = 1:N
                    sum = sum + (X(m,n) * cos(pi*(2*m-1)*p/(2*M)) * cos(pi*(2*n-1)*q/(2*N))); 
                end
            end
            Y(p+1,q+1) = Ap * Aq * sum;
        end
    end
end


%2-D Inverse DCT function
function Y = fIDct2(X)
    
    %Determine the dimensions of the Image
    [M,N] = size(X);
    Y = zeros(size(X));

    for m = 0:M-1    
        for n = 0:N-1
            sum = 0;
            for p = 0:M-1
                if (p == 0)
                    Ap = 1/sqrt(M);
                else
                    Ap = sqrt(2/M);
                end
                for q = 0:N-1
                    if (q == 0)
                        Aq = 1/sqrt(N);
                    else
                        Aq = sqrt(2/N);
                    end    
                    sum = sum + (Ap * Aq * X(p+1,q+1) * cos(pi*(2*m+1)*p/(2*M)) * cos(pi*(2*n+1)*q/(2*N))); 
                end
            end
            Y(m+1,n+1) = sum;
        end
    end
end

%Function to calculate Mean, Standard Deviation & Step-size
function [mean8x8,std8x8,step8x8] = fcalMeanSdStepsize(X)
    
    [M,N] = size(X);
    m = 8;      %No. of rows in the block (=8 for 8X8 block)
    n = 8;      %No. of columns in the block (=8 for 8X8 block)
    if (M == N)
        %Re-arrange the frequency components of the Image by grouping the 
        %equivalent frequencies together i.e. DC component (lowest
        %frequency) from each block arranged in the 1st row followed by
        %AC components (high frequencies) in the 2nd row and so on.
        %Resulting matrix is 64 X 4096
        for i = 0:(m*n-1)
            fun = @(block_struct) reshape(block_struct.data',[64 1]);
            tempY = blockproc(X(8*i+1:8*i+8,:),[8 8],fun);
            if (i==0)
                Y = tempY;
            else
                Y = horzcat(Y,tempY);
            end
        end
        
        %Mean, SD & Step-size for each of the 64 elements in the 8X8 block
        mean_x = zeros(64,1);
        std_x = zeros(64,1);
        step_x = zeros(64,1);
        
        for i = 1:m*n
            mean_x(i,1) = mean(Y(i,:));     %Calculate Mean of 1-D array
            std_x(i,1) = std(Y(i,:));       %Calculate Standard Deviation of 1-D array
            %Calculate Step-size using 10 bits
            step_x(i,1) = 4*std_x(i,1)/(2^10);
        end
        mean8x8 = reshape(mean_x,[8 8])';   %Mean formatted into 8X8 block
        std8x8 = reshape(std_x,[8 8])';     %SD formatted into 8X8 block
        step8x8 = reshape(step_x,[8 8])';   %Step-size formatted into 8X8 block
    else
        disp('Error: Dimensions mis-match');
    end
end

%Function to Normalize and Quantize
function Y = fNormQuantize(X,mean8x8,std8x8,step8x8)
    
    Y = zeros(8,8);
    for i = 1:8
        for j = 1:8
           if (std8x8(i,j) == 0) 
               Y(i,j) = 0;
           else
               Y(i,j) = round((X(i,j)-mean8x8(i,j))/(step8x8(i,j)*std8x8(i,j)));
           end
        end
    end
end

%Function to compute 2-D DFT
function Y = fDft2(X)
    
    %Determine the dimensions of the Image
    [M,N] = size(X);
    Y = zeros(M,N);

    %Compute the 1-D FFT of the Image
    for i = 1:M
        Y(i,:) = fft(X(i,:));
    end

    %Re-compute the 1-D FFT of the Image
    for j = 1:N
        Y(:,j) = fft(Y(:,j));
    end
    
    %Shift the zero-frequency component to center of spectrum
    tempY = fftshift(Y);

    %Obtain the Magnitude Spectrum
    Y = log(1+abs(tempY));
end

%Function to calculate Total no. of bits to code the Image & Average number of
%bits/pixel
function [totBits,avgBitsPerPixel] = fCalTotAvgBits(X)
    
    [M,N] = size(X);
    noOfNonZeroElements = nnz(X);
    totBits = noOfNonZeroElements * 8;
    avgBitsPerPixel = totBits / (M*N);
    
end

%Function to calculate PSNR
function psnrValue = fCalPsnr(noisyImage,orgImage)

    %Determine the dimensions of the Noisy Image
    [M,N] = size(noisyImage);

    %Compute the difference between Original Image & Noisy Image
    difImage = orgImage - noisyImage;

    %Compute the Mean Square Error
    difImage = difImage .* difImage;
    sumInt = sum(sum(difImage));
    mseVal = sumInt/(M*N);

    %Finding out the maximum value of Pixel in Original Image
    maxPixelOrgImage = max(max(orgImage));

    %Calculate PSNR
    psnrValue = 10*log10((maxPixelOrgImage*maxPixelOrgImage)/mseVal);
    
end