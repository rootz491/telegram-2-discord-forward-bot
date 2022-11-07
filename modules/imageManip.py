import cv2
from os import getcwd

def add_watermark(image):

  watermark = cv2.imread(getcwd() + "/modules/watermark.png")

  wm_scale = 35
  wm_width = int(watermark.shape[1] * wm_scale / 100)
  wm_height = int(watermark.shape[0] * wm_scale / 100)
  wm_dim = (wm_width, wm_height)
  wm_resized = cv2.resize(watermark, wm_dim, interpolation = cv2.INTER_AREA)

  h_img, w_img, _ = image.shape
  h_wm, w_wm, _ = wm_resized.shape

  margin = 10

  top_y = h_img - h_wm - margin
  left_x = w_img - w_wm - margin
  bottom_y = top_y + h_wm
  right_x = left_x + w_wm
  

  # Create a ROI
  roi = image[top_y:bottom_y, left_x:right_x]
  result = cv2.addWeighted(roi, 1, wm_resized, 0.6, 0)

  image[top_y:bottom_y, left_x:right_x] = result

  cv2.destroyAllWindows()

  return image


if __name__ == "__main__":
  print(getcwd())
  image = cv2.imread(getcwd() + "/modules/image.jpg")
  newImg = add_watermark(image)
  cv2.imwrite(getcwd() + "/modules/newImg.jpg", newImg)
  cv2.imshow("Resized Input Image", newImg)

