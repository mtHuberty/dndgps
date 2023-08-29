import pyautogui
import cv2
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import ImageGrab
from functools import partial

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

def find_best_matching_template():
    try:
        # Capture the screenshot
        screenshot = pyautogui.screenshot()

        # Crop to the minimap
        x = 2550 - 327
        y = 1440 - 336
        length = 290
        cropped_screenshot = screenshot.crop((x, y, x + length, y + length))
        cropped_screenshot = cv2.cvtColor(np.array(cropped_screenshot), cv2.COLOR_RGB2BGR)

        # Load SIFT detector
        orb = cv2.ORB_create()

        map_paths = ["crypt-1-normal.png", "crypt-2-normal.png", "crypt-3-normal.png"]

        best_score = 0
        best_map_path = None
        best_matches = None

        for map_path in map_paths:
            # Load the template image
            map = cv2.imread(map_path, cv2.IMREAD_GRAYSCALE)

            # Find keypoints and descriptors using ORB
            kp1, des1 = orb.detectAndCompute(map, None)
            kp2, des2 = orb.detectAndCompute(cropped_screenshot, None)

            # Create BFMatcher object
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

            # Match descriptors
            matches = bf.match(des1, des2)

            # Sort matches by distance
            matches = sorted(matches, key=lambda x: x.distance)

            # Only keep really good matches
            good_matches = [m for m in matches if m.distance < 50]

            if len(good_matches) > best_score:
                best_score = len(good_matches)
                best_map_path = map_path
                best_matches = good_matches[:10]

        if best_map_path:
            print("Found map:", best_map_path)
            print("Number of good matches:", best_score)

            # Load the template image for drawing bounding box
            src_pts = np.float32([kp1[m.queryIdx].pt for m in best_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in best_matches]).reshape(-1, 1, 2)
            _, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            pts = src_pts[mask==1]
            min_x, min_y = np.int32(pts.min(axis=0))
            max_x, max_y = np.int32(pts.max(axis=0))

            # Draw bounding box around matched region on the best map
            print("Bounding...")
            best_map = cv2.imread(best_map_path)
            best_map_with_bounding_box = cv2.rectangle(best_map, (min_x, min_y), (max_x, max_y), (0, 0, 255), 3)

            # Get map name without file extension
            print("Getting map name...")
            last_dot_index = best_map_path.rfind(".")
            best_map_name = best_map_path[:last_dot_index]

            # Display the result
            print("Displaying map...")
            cv2.imshow(best_map_name, best_map_with_bounding_box)

            # Open interactive map page
            driver = webdriver.Chrome()
            print("Opening interactive map...")
            url = f"https://mapgenie.io/dark-and-darker/maps/{best_map_name}"
            driver.get(url)

            # Find an element by its name (e.g., search bar)
            hide_all_link = driver.find_element(By.CSS_SELECTOR, "#hide-all")
            hide_all_link.click()

            # Show Shrines of Health
            title_elements = driver.find_elements(By.CSS_SELECTOR, ".title")
            for element in title_elements:
                if element.text == "Shrine of Health":
                    element.click()
                    break

            # Keep cv2 image open
            cv2.waitKey(0)
            # cv2.destroyAllWindows()
        else:
            print("No matching template found")

    except Exception as e:
        print("Error:", e)

find_best_matching_template()
