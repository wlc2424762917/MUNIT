import numpy as np
import os
import numpy as np
from glob import glob
from skimage.transform import resize
import SimpleITK as sitk
from matplotlib import pylab as plt
import nibabel as nib
from collections import OrderedDict
from skimage.morphology import label
import pickle
from scipy.ndimage import zoom
import math
import cv2


def calculate_psnr(img1, img2):
    # img1 and img2 have range [0, 255]
    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    mse = np.mean((img1 - img2)**2)
    if mse == 0:
        return float('inf')
    return 20 * math.log10(255.0 / math.sqrt(mse))


def ssim_computation(img1, img2):
    C1 = (0.01 * 255)**2
    C2 = (0.03 * 255)**2

    img1 = img1.astype(np.float64)
    img2 = img2.astype(np.float64)
    kernel = cv2.getGaussianKernel(11, 1.5)
    window = np.outer(kernel, kernel.transpose())

    mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]  # valid
    mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]
    mu1_sq = mu1**2
    mu2_sq = mu2**2
    mu1_mu2 = mu1 * mu2
    sigma1_sq = cv2.filter2D(img1**2, -1, window)[5:-5, 5:-5] - mu1_sq
    sigma2_sq = cv2.filter2D(img2**2, -1, window)[5:-5, 5:-5] - mu2_sq
    sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) *
                                                            (sigma1_sq + sigma2_sq + C2))
    return ssim_map.mean()


def calculate_ssim(img1, img2):
    '''calculate SSIM
    the same outputs as MATLAB's
    img1, img2: [0, 255]
    '''
    if not img1.shape == img2.shape:
        raise ValueError('Input images must have the same dimensions.')
    if img1.ndim == 2:
        return ssim_computation(img1, img2)
    elif img1.ndim == 3:
        if img1.shape[2] == 3:
            ssims = []
            for i in range(3):
                ssims.append(ssim(img1, img2))
            return np.array(ssims).mean()
        elif img1.shape[2] == 1:
            return ssim_computation(np.squeeze(img1), np.squeeze(img2))
    else:
        raise ValueError('Wrong input image dimensions.')


if __name__ == '__main__':
    path_infer = r"C:\Users\wlc\PycharmProjects\pytorch-CycleGAN-and-pix2pix\results_npy"
    path_gt = r"D:\style_transfer_divided_unpaired\testB"

    path_gts = []
    path_infers = []
    for root, _, fnames in sorted(os.walk(path_gt)):
        for fname in fnames:
            path = os.path.join(root, fname)
            path_gts.append(path)
    print(path_gts)
    print(len(path_gts))

    for root, _, fnames in sorted(os.walk(path_infer)):
        for fname in fnames:
            path = os.path.join(root, fname)
            path_infers.append(path)
    print(path_infers)
    print(len(path_infers))

    psnrs = []
    ssims = []
    for idx, (infer_img_path, gt_img_path) in enumerate(zip(path_infers, path_gts)):
        print(f"{idx}: {infer_img_path}, {gt_img_path}.")
        infer_img = np.load(infer_img_path, allow_pickle=True)
        #print(infer_img.shape)
        gt_img = np.load(gt_img_path, allow_pickle=True)

        zoom_scale_H, zoom_scale_W = infer_img.shape[0]/gt_img.shape[0], infer_img.shape[1]/gt_img.shape[1]
        gt_img = zoom(gt_img, zoom=[zoom_scale_H, zoom_scale_W], order=3)
        #print(gt_img.shape)
        psnr, ssim = calculate_psnr(infer_img, gt_img), calculate_ssim(infer_img, gt_img)
        print(f"PSNR: {psnr}, SSIM: {ssim}")
        psnrs.append(psnr)
        ssims.append(ssim)






# def read_img(mod_1_path, mod_2_path, src_file_name, mod_1_save_path, mod_2_save_path, mod_12_save_path, gt_file_path, gt_file_name, gt_save_path):  # for .mhd .nii .nrrd
#     '''
#     N*h*W
#     :param full_path_filename:
#     :return:*H*W
#     '''
#     if not os.path.exists(mod_1_path):
#         raise FileNotFoundError
#     mod_1_data = nib.load(mod_1_path).get_fdata()
#     mod_2_data = nib.load(mod_2_path).get_fdata()
#
#     mod_1_data_norm = (mod_1_data - mod_1_data.mean()) / (mod_1_data.std())  # case norm
#     mod_2_data_norm = (mod_2_data - mod_2_data.mean()) / (mod_2_data.std())
#
#     mod_1_data_norm = ((mod_1_data - mod_1_data.min()) / (mod_1_data.max() - mod_1_data.min())) * 255  # case norm
#     mod_2_data_norm = ((mod_2_data - mod_2_data.min()) / (mod_2_data.max() - mod_2_data.min())) * 255
#
#     print(src_file_name, " data_shape:", mod_1_data_norm.shape)
#     print(mod_1_data_norm.max())
#     if not os.path.exists(gt_file_path):
#         raise FileNotFoundError
#
#     mask_data = nib.load(gt_file_path).get_fdata()
#     mask_data_norm = mask_data  # no case norm for gt_seg
#
#     save_mod_1_path_npy = mkdir(os.path.join(mod_1_save_path, src_file_name))
#     save_mod_2_path_npy = mkdir(os.path.join(mod_2_save_path, src_file_name))
#     save_mod_12_path_npy = mkdir(os.path.join(mod_12_save_path, src_file_name))
#     save_gt_path_npy = mkdir(os.path.join(gt_save_path, gt_file_name))
#
#     num_slices = 0
#     for slice_idx in range(0, mask_data_norm.shape[2]):
#         mod_1_slice = mod_1_data_norm[:, :, slice_idx].reshape((1, 240, 240))
#         mod_2_slice = mod_2_data_norm[:, :, slice_idx].reshape((1, 240, 240))
#         combine_slice = np.concatenate((mod_1_slice, mod_2_slice), axis=1)
#         mask_slice = mask_data_norm[:, :, slice_idx]
#         mask_slice = grayval2label(mask_slice)
#
#         num_slices += 1
#         np.save(os.path.join(save_mod_1_path_npy, '{}_{:03d}.npy'.format(src_file_name, slice_idx)), mod_1_slice)
#         np.save(os.path.join(save_mod_2_path_npy, '{}_{:03d}.npy'.format(gt_file_name, slice_idx)), mod_2_slice)
#         np.save(os.path.join(save_mod_12_path_npy, '{}_{:03d}.npy'.format(gt_file_name, slice_idx)), combine_slice)
#         np.save(os.path.join(save_gt_path_npy, '{}_{:03d}.npy'.format(gt_file_name, slice_idx)), mask_slice)
#
#         num_slices += 1
#     print(num_slices)
#
#
# # def read_img(mod_1_path, mod_2_path, src_file_name, mod_1_save_path, mod_2_save_path, mod_12_save_path, gt_file_path, gt_file_name, gt_save_path):  # for .mhd .nii .nrrd
#
# def read_dataset(mod_1_paths, mod_2_paths, gt_file_paths, mod_1_save_path, mod_2_save_path, mod_12_save_path, gt_save_path):
#     for idx_data in range(len(mod_1_paths)):
#         print('{} / {}'.format(idx_data + 1, len(mod_1_paths)))
#         mod_1_path = mod_1_paths[idx_data]
#         mod_2_path = mod_2_paths[idx_data]
#         mask_path = gt_file_paths[idx_data]
#
#         nameext, _ = os.path.splitext(mod_1_path)
#         nameext, _ = os.path.splitext(nameext)
#
#         mask_nameext, _ = os.path.splitext(mask_path)
#         mask_nameext, _ = os.path.splitext(mask_nameext)
#
#         _, name = os.path.split(nameext)
#         src_name = name[:-6]
#         _, mask_name = os.path.split(mask_nameext)
#         print(mask_name)
#         print(src_name)
#
#         read_img(mod_1_path, mod_2_path, src_name, mod_1_save_path, mod_2_save_path, mod_12_save_path, mask_path, mask_name, gt_save_path)
#
#
# def mkdir(path):
#     if not os.path.exists(path):
#         os.makedirs(path)
#     return path
#
#
# if __name__ == '__main__':
#
#     # path_raw_dataset_type = r"D:\braTS_t"
#     # mod_1_path_save = mkdir(r"D:\style_transfer_test\A")
#     # mod_12_path_save = mkdir(r"D:\style_transfer_test\AB")
#     # mod_2_path_save = mkdir(r"D:\style_transfer_test\B")
#     # gt_path_save = mkdir(r"D:\style_transfer_test\gt")
#
#     path_raw_dataset_type = "/media/NAS02/BraTS2020/Training/"
#     mod_1_path_save = mkdir("/media/NAS02/BraTS2020/pix2pix_cycle/A")
#     mod_12_path_save = mkdir("/media/NAS02/BraTS2020/pix2pix_cycle/AB")
#     mod_2_path_save = mkdir("/media/NAS02/BraTS2020/pix2pix_cycle/B")
#     gt_path_save = mkdir("/media/NAS02/BraTS2020/pix2pix_cycle/gt")
#
#     mask_paths = []
#     t2_paths = []
#     t1_paths = []
#     t1ce_paths = []
#     flair_paths = []
#     start = 151
#     start = 0
#     for p_id in range(start, 1667):
#         p_id_str = str(p_id)
#         path_raw_dataset_type_patient = os.path.join(path_raw_dataset_type, 'BraTS20_Training_'+p_id_str.zfill(3))
#         # print(path_raw_dataset_type_patient)
#         flair_paths.extend(glob(os.path.join(path_raw_dataset_type_patient, '*flair.nii')))
#         t1_paths.extend(glob(os.path.join(path_raw_dataset_type_patient, '*t1.nii')))
#         t1ce_paths.extend(glob(os.path.join(path_raw_dataset_type_patient, '*t1ce.nii')))
#         t2_paths.extend(glob(os.path.join(path_raw_dataset_type_patient, '*t2.nii')))
#         mask_paths.extend(glob(os.path.join(path_raw_dataset_type_patient, '*seg.nii')))
#
#     print(flair_paths)
#     print(len(flair_paths))
#
#     read_dataset(flair_paths, t1_paths, mask_paths, mod_1_path_save, mod_2_path_save, mod_12_path_save, gt_path_save)
#
