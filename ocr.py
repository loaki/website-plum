import cv2
import pytesseract
#import easyocr
import sys

def ocr(file_name):
    #tesseract OCR
    # https://github.com/UB-Mannheim/tesseract/wiki
    
    #pytesseract.pytesseract.tesseract_cmd = 'Tesseract-OCR/tesseract.exe'
    #pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
    customconf = """-c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'- " --psm 6"""
    ocr_text = pytesseract.image_to_string(file_name, config=customconf)
    return(ocr_text.replace('\n\f', ''))
    #reader = easyocr.Reader(['en'])
    #return(reader.readtext(file_name)[0][1])

def img_to_str(img):
    img_final = img
    img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(img2gray, 180, 255, cv2.THRESH_BINARY)
    image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
    ret, new_img = cv2.threshold(image_final, 180, 255, cv2.THRESH_BINARY)  # for black text , cv.THRESH_BINARY_INV
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))  # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
    dilated = cv2.dilate(new_img, kernel, iterations=6)  # dilate , more the iteration more the dilation
    # for cv2.x.x
    contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # findContours returns 3 variables for getting contours
    # for cv3.x.x comment above line and uncomment line below
    #image, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    text_list = []
    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)
        #players 9 
        if (x / img.shape[1] * 100) > 7 and (x / img.shape[1] * 100) < 15 and (w / img.shape[1] * 100) > 3 and (h / img.shape[0] * 100) > 2:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cropped = img_final[y :y +  h , x : x + w]
            cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            text_list.append(ocr(cropped))
            #print('img w=',img.shape[1], 'img h=',img.shape[0], '| x=', x,'| y=', y, '| w=', w,'| h=', h, '|', ocr(cropped))

        #victory/defeat 3
        elif (x / img.shape[1] * 100) > 1 and (x / img.shape[1] * 100) < 5 and (w / img.shape[1] * 100) > 5 and (y / img.shape[0] * 100) < 6:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cropped = img_final[y :y +  h , x : x + w]
            #cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            cv2.imwrite('163dsfg-fail.png' , cropped)
            text_list.append(ocr(cropped))
            #print('img w=',img.shape[1],'img h=',img.shape[0], '| x=', x,'| y=', y, '| w=', w,'| h=', h, '|', ocr(cropped))

        #winners/loosers 5
        elif (x / img.shape[1] * 100) > 4 and (x / img.shape[1] * 100) < 8 and (w / img.shape[1] * 100) > 5 and (h / img.shape[0] * 100) > 2:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cropped = img_final[y :y +  h , x : x + w]
            cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            text_list.append(ocr(cropped))
            #print('img w=',img.shape[1],'img h=',img.shape[0], '| x=', x,'| y=', y, '| w=', w,'| h=', h, '|', ocr(cropped))

        else:
            cv2.rectangle(img, (x, y), (x + w, y + h), (100, 100, 100), 2)
        ''' cropped = img_final[y :y +  h , x : x + w]
            cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            print('img w=',img.shape[1], 'img h=',img.shape[0], '| x=', x,'| y=', y, '| w=', w,'| h=', h, '|', ocr(cropped))'''

    #write original image with added contours to disk
    #text_list.reverse()
    #print(text_list)
    #cv2.imshow('captcha_result', img)
    #cv2.waitKey()
    #cv2.imwrite('ocr.png' , img)
    text_list.reverse()
    return(text_list)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else :
        print('no file specified')
    image = cv2.imread(file_name)
    print(img_to_str(image))