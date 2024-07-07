#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def parzen(x, x_trn, h):
    """
    p = parzen(x, x_trn, h)

    Parzen window density estimation with normal kernel N(0, h^2).

    :param x:       vector of data points where the probability density functions
                    should be evaluated, (n,) np array
    :param x_trn:   training data (m,) np array
    :param h:       kernel bandwidth, python float
    :return p:      estimated p(x|k) evaluated at values given by x (n,) np array
    """

    p = np.zeros(x.shape[0])

    for i in range(x.shape[0]):
        delta_x = x[i] - x_trn
        Khx = norm.pdf(delta_x,loc=0,scale=h)
        p[i] = np.mean(Khx)

    return p


def compute_Lh(itrn, itst, x, h):
    """
    Lh = compute_Lh(itrn, itst, x, h)

    Computes the average log-likelihood over training/test splits generated
    by crossval for a fixed kernel bandwidth h.

    :param itrn:    LIST of (n,) np arrays data splits (indices) generated by crossval()
    :param itst:    LIST of (m,) np arrays data splits (indices) generated by crossval()
    :param x:       input data (n+m,) np array
    :param h:       kernel bandwidth, python float
    :return Lh:     average log-likelihood over training/test splits, python float
    """

    Lh_lst = np.zeros(len(itrn))
    for i in range(len(itrn)): # indexes
        x_trn = x[itrn[i]]
        x_tst = x[itst[i]]

        Lh_lst[i] = np.sum(np.log(parzen(x_tst,x_trn,h)))
    Lh = np.mean(Lh_lst)

    return Lh


def classify_bayes_parzen(x_test, xA, xC, pA, pC, h_bestA, h_bestC):
    """
    labels = classify_bayes_parzen(x_test, xA, xC, pA, pC, h_bestA, h_bestC)

    Classifies data using bayesian classifier with densities estimated by
    Parzen window estimator.

    :param x_test:  data (measurements) to be classified (n,) np array
    :param xA:      training data for Parzen window for class A (n_xA,) np array
    :param xC:      training data for Parzen window for class C (n_xC,) np array
    :param pA:      prior probability for class A, python float
    :param pC:      prior probability for class C, python float
    :param h_bestA: optimal value of the kernel bandwidth, python float
    :param h_bestC: optimal value of the kernel bandwidth, python float
    :return labels: classification labels for x_test (n,) np array
    """

    prob_A = parzen(x_test,xA,h_bestA)
    prob_C = parzen(x_test,xC,h_bestC)
    R_A = prob_C * pC
    R_C = prob_A * pA
    labels = R_C < R_A
    
    return labels


################################################################################
#####                                                                      #####
#####             Below this line are already prepared methods             #####
#####                                                                      #####
################################################################################


def show_classification(test_images, labels, letters):
    """
    show_classification(test_images, labels, letters)

    create montages of images according to estimated labels

    :param test_images:     np.array (h, w, n)
    :param labels:          labels for input images np.array (n,)
    :param letters:         string with letters, e.g. 'CN'
    """

    def montage(images, colormap='gray'):
        """
        Show images in grid.

        :param images:      np.array (h, w, n)
        :param colormap:    numpy colormap
        """
        h, w, count = np.shape(images)
        h_sq = int(np.ceil(np.sqrt(count)))
        w_sq = h_sq
        im_matrix = np.zeros((h_sq * h, w_sq * w))

        image_id = 0
        for j in range(h_sq):
            for k in range(w_sq):
                if image_id >= count:
                    break
                slice_w = j * h
                slice_h = k * w
                im_matrix[slice_h:slice_h + w, slice_w:slice_w + h] = images[:, :, image_id]
                image_id += 1
        plt.imshow(im_matrix, cmap=colormap)
        plt.axis('off')
        return im_matrix

    for i in range(len(letters)):
        imgs = test_images[:,:,labels==i]
        subfig = plt.subplot(1,len(letters),i+1)
        montage(imgs)
        plt.title(letters[i])


def crossval(num_data, num_folds):
    """
    itrn, itst = crossval(num_data, num_folds)

    Partitions data for cross-validation.

    This function randomly partitions data into the training
    and testing parts. The number of partitioning is determined
    by the num_folds. If num_folds==1 then makes only one random
    partitioning of data into training and testing in ratio 50:50.

    :param num_data:    number of data (scalar, integer)
    :param num_folds:   number of folders (scalar, integer)
    :return itrn:       itrn - LIST of training folds, itst - LIST of testing folds
                            itrn[i] indices of training data of i-th folder (n,) np array
                            itst[i] indices of testing data of i-th folder (n,) np array
    """
    if num_folds < 2:
        print("Minimal number of folds set to 2.")
        num_folds = 2

    inx = np.random.permutation(num_data)

    itrn = []
    itst = []

    num_column = np.int32(np.ceil(np.float64(num_data) / num_folds))

    for idx in range(num_folds):
        tst_idx = range((idx * num_column), np.min([num_data, ((idx + 1) * num_column)]))
        trn_idx = [i for i in list(range(num_data)) if i not in tst_idx]
        itst.append(inx[tst_idx])
        itrn.append(inx[trn_idx])
    return itrn, itst


def compute_measurement_lr_cont(imgs):
    """
    x = compute_measurement_lr_cont(imgs)

    Compute measurement on images, subtract sum of right half from sum of
    left half.

    :param imgs:    set of images, (h, w, n)
    :return:        measurements, (n, )
    """
    assert len(imgs.shape) == 3

    width = imgs.shape[1]
    sum_rows = np.sum(imgs, dtype=np.float64, axis=0)

    x = np.sum(sum_rows[0:int(width / 2),:], axis=0) - np.sum(sum_rows[int(width / 2):,:], axis=0)

    assert x.shape == (imgs.shape[2], )
    return x


################################################################################
#####                                                                      #####
#####             Below this line you may insert debugging code            #####
#####                                                                      #####
################################################################################

def main():
    # HERE IT IS POSSIBLE TO ADD YOUR TESTING OR DEBUGGING CODE
    pass

if __name__ == "__main__":
    main()
