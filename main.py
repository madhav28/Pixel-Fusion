import os
import cv2
import numpy as np

os.makedirs("./results/unaligned", exist_ok=True)
os.makedirs("./results/aligned", exist_ok=True)

def combine_image(img_path, out_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    h = img.shape[0]//3
    
    b_c = img[8:h, :]
    g_c = img[h+4:2*h-4, :]
    r_c = img[2*h:3*h-8, :]

    img = cv2.merge([b_c, g_c, r_c])

    cv2.imwrite(out_path, img)

def normalized_cross_correlation(C1, C2):
    C1_mean = C1 - np.mean(C1)
    C2_mean = C2 - np.mean(C2)
    return np.sum(C1_mean * C2_mean) / np.sqrt(np.sum(C1_mean ** 2) * np.sum(C2_mean ** 2))

def get_offsets(C1, C2):
    max_prod = -1
    x_offset = -1
    y_offset = -1
    for i in range(-15, 16):
        for j in range(-15, 16):
            curr_prod = normalized_cross_correlation(np.roll(C1, (i, j), axis=(0, 1)), C2)
            if curr_prod > max_prod:
                x_offset = i
                y_offset = j
                max_prod = curr_prod
    return x_offset, y_offset

if __name__ == "__main__":
    img_paths = ["prokudin-gorskii/" + filename for filename in os.listdir("prokudin-gorskii/") if filename.endswith('.jpg')]
    unaligned_img_paths = []
    for img_path in img_paths:
        out_path = "./results/unaligned/"+img_path.split("/")[-1]
        unaligned_img_paths.append(out_path)
        combine_image(img_path, out_path)
        
    for img_path in unaligned_img_paths:
        img = cv2.imread(img_path)
        
        b_c = img[:, :, 0]
        g_c = img[:, :, 1]
        r_c = img[:, :, 2]

        x1_offset, y1_offset = get_offsets(b_c, r_c)
        x2_offset, y2_offset = get_offsets(g_c, r_c)

        print(img_path)
        print(f'Red Channel offset: (x, y) = (0, 0)')
        print(f'Blue Channel offset: (x, y) = ({x1_offset}, {y1_offset})')
        print(f'Green Channel offset: (x, y) = ({x2_offset}, {y2_offset})')
        print()

        b_c = np.roll(b_c, (x1_offset, y1_offset), axis=(0, 1))
        g_c = np.roll(g_c, (x2_offset, y2_offset), axis=(0, 1))

        img = cv2.merge([b_c, g_c, r_c])

        cv2.imwrite(img_path.replace('unaligned', 'aligned'), img)