
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3



def image_to_text(path):

    input_imge=Image.open(path)

    #converting image to array format

    image_arr=np.array(input_imge)

    reader=easyocr.Reader(['en'])
    text=reader.readtext(image_arr,detail= 0)

    return text , input_imge

def extracted_text(texts):

  extrad_dic={"NAME":[], "DESIGNATION":[], "COMPANYNAME": [],"CONTACT": [] ,"EMAIL":[],"WEBSITE": [] , "ADDRESS" :[],"PINCODE" :[]}

  extrad_dic["NAME"].append(texts[0])
  extrad_dic["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):

    if texts[i].startswith("+" or (texts)[i].replace("-","").isdigit() and '-' in texts[i]):

      extrad_dic["CONTACT"].append(texts[i])

    elif "@"  in texts[i] and ".com" in texts[i]:
      extrad_dic["EMAIL"].append(texts[i])

    elif "WWW"  in texts[i] or "www" in texts[i] or "Www"  in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small= texts[i].lower()
      extrad_dic["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extrad_dic["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]', texts[i]):
      extrad_dic["COMPANYNAME"].append(texts[i])

    else:
      remove_colon= re.sub(r'[,;]', '',texts[i])
      extrad_dic["ADDRESS"].append(texts[i])

  for key,value in extrad_dic.items():
    if len(value)>0:
      concadenate=" ".join(value)
      extrad_dic[key]=[concadenate]
    else:
      value = "NA"
      extrad_dic[key]=[value]


  return extrad_dic


#streamlit part

st.set_page_config(layout = "wide")
st.markdown("<h1 style='text-align: center; color: #a88132;'>Business Card Data Extraction</h1>", unsafe_allow_html=True)

select= option_menu(
        menu_title = None,
        options = ["HOME","UPLOAD AND MODIFYING", "DELETE"],
        icons =["database","vector-pen","eraser"],
        default_index=0,
        orientation="horizontal",
        styles={"container": {"padding": "0!important", "background-color": "#32a842","size":"cover", "width": "100%"},
                "icon": {"color": "#a8328c", "font-size": "20px"},
                "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#3232a8"},
                "nav-link-selected": {"background-color": "#b0abac"}})


if select == "HOME":
    st.subheader("About the Application")
    st.write(" Users can save the information extracted from the card image using easy OCR. The information can be uploaded into a database (MySQL) after alterations that supports multiple entries. ")
    st.subheader("What is Easy OCR?")
    st.write("Easy OCR is user-friendly Optical Character Recognition (OCR) technology, converting documents like scanned paper, PDFs, or digital camera images into editable and searchable data. A variety of OCR solutions, including open-source libraries, commercial software, and cloud-based services, are available. These tools are versatile, used for extracting text from images, recognizing printed or handwritten text, and making scanned documents editable.")
    
   
elif select == "UPLOAD AND MODIFYING":

  img=st.file_uploader("Upload the Image",type=["png","jpg","jpeg"])

  if img is not None:
    st.image(img,width=300)

    text_image,input_imge= image_to_text(img)

    text_dict=extracted_text(text_image)

    if text_dict:
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")

    df= pd.DataFrame(text_dict)



    image_bytes=io.BytesIO()
    input_imge.save(image_bytes, format= "PNG")

    image_data=image_bytes.getvalue()

    #creating Dictionary

    data= {"IMAGE":[image_data]}

    df_1=pd.DataFrame(data)

    con_df= pd.concat([df,df_1] ,axis=1)

    st.dataframe(con_df)

    button_1= st.button("Save",use_container_width=True)


    if button_1:

      mydb=sqlite3.connect("bizcard.db")
      cursor=mydb.cursor()

      #Table Creation

      create_table = ''' CREATE TABLE IF NOT EXISTS bizcard_details(name vachar(225),
                                                              designation varchar(225),
                                                              company_name varchar(225),
                                                              contact varchar(225),
                                                              email varchar(225),
                                                              website text,
                                                              address text,
                                                              pincode  varchar(225),
                                                              image text)'''

      cursor.execute(create_table)
      mydb.commit()

    #Insert Query

      insert_table = ''' INSERT INTO bizcard_details(name,designation,company_name,contact,email,website,address,
                                                            pincode,image)

                                                            values(?,?,?,?,?,?,?,?,?)'''

      data1 = con_df.values.tolist()[0]
      cursor.execute(insert_table,data1)
      mydb.commit()
      st.success("Save successfully")


  method1=st.radio("Select The Method",["None","Preview","Modify"])
  if method1== "None":
    st.write("")

  if method1 == "Preview":

    mydb=sqlite3.connect("bizcard.db")
    cursor=mydb.cursor()

    #select query

    select_table="SELECT * FROM bizcard_details"

    cursor.execute(select_table)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table,columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE","ADDRESS",
                                          "PINCODE","IMAGE"))
    st.dataframe(table_df)

  elif method1 == "Modify":

    mydb=sqlite3.connect("bizcard.db")
    cursor=mydb.cursor()

    #select query

    select_table="SELECT * FROM bizcard_details"

    cursor.execute(select_table)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table,columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE","ADDRESS",
                                          "PINCODE","IMAGE"))
    col1,col2 = st.columns(2)
    with col1:

      sel_name = st.selectbox("Select the name", table_df["NAME"])

    df_3 = table_df[table_df["NAME"] == sel_name]

    st.dataframe(df_3)

    df_4 = df_3.copy()

    st.dataframe(df_4)

    col1,col2 = st.columns(2)
    with col1:
      mo_name = st.text_input("Name" ,df_3["NAME"].unique()[0])
      mo_des = st.text_input("Designation" ,df_3["DESIGNATION"].unique()[0])
      mo_co = st.text_input("Company_name" ,df_3["COMPANY_NAME"].unique()[0])
      mo_cont = st.text_input("Contact" ,df_3["CONTACT"].unique()[0])
      mo_email = st.text_input("Email" ,df_3["EMAIL"].unique()[0])

      df_4["NAME"] = mo_name
      df_4["DESIGNATION"] = mo_des
      df_4["COMPANY_NAME"] = mo_co
      df_4["CONTACT"] = mo_cont
      df_4["EMAIL"] = mo_email

      mo_web = st.text_input("Website" ,df_3["WEBSITE"].unique()[0])
      mo_add = st.text_input("Address" ,df_3["ADDRESS"].unique()[0])
      mo_pin = st.text_input("Pincode" ,df_3["PINCODE"].unique()[0])
      mo_img = st.text_input("Image" ,df_3["IMAGE"].unique()[0])

      df_4["WEBSITE"] = mo_web
      df_4["ADDRESS"] = mo_add
      df_4["PINCODE"] = mo_pin
      df_4["IMAGE"] = mo_img

    st.dataframe(df_4)

    col1,col2 = st.columns(2)
    with col1:
      button_3 = st.button("Modify",use_container_width = True)

    if button_3:

      mydb = sqlite3.connect("bizcard.db")
      cursor = mydb.cursor()

      cursor.execute(f"DELETE FROM bizcard_details where NAME='{sel_name}'")
      mydb.commit()

      insert_table = ''' INSERT INTO bizcard_details(name,designation,company_name,contact,email,website,address,
                                                              pincode,image)

                                                              values(?,?,?,?,?,?,?,?,?)'''

      data1 = df_4.values.tolist()[0]
      cursor.execute(insert_table,data1)
      mydb.commit()

      st.success("Modified Successfully")








elif select == "DELETE":

      mydb = sqlite3.connect("bizcard.db")
      cursor = mydb.cursor()
      st.subheader(":black[Delete the data]")

      try:

          cursor.execute(f"SELECT NAME FROM bizcard_details")
          result = cursor.fetchall()
          mydb.commit()
          business_cards = {}

          for row in result:
            business_cards[row[0]] = row[0]
            options = ["None"] + list(business_cards.keys())
            selected_card = st.selectbox("**Select a card**", options)
            if selected_card == "None":
               st.write("No card selected")
          else:
                st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
                st.write("#### Proceed to delete this card?")
                if st.button("Confirm deletion"):
                    cursor.execute(f"DELETE FROM bizcard_details WHERE NAME='{selected_card}'")
                    mydb.commit()
                    st.success("Business card information has been deleted from database")

          if st.button(":black[View data]"):
              mydb=sqlite3.connect("bizcard.db")
              select_table="SELECT * FROM bizcard_details"

              cursor.execute(select_table)
              table = cursor.fetchall()
              mydb.commit()

              table_df = pd.DataFrame(table,columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","EMAIL","WEBSITE","ADDRESS",
                                                    "PINCODE","IMAGE"))
              st.dataframe(table_df)

    
      except:

        st.warning("There is no data available in the database")



