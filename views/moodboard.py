# # import logging
# # import streamlit as st
# # import os
# # from PIL import Image
# # import pandas as pd
# # from sqlalchemy import create_engine, text
# # from google.cloud import storage
# # from io import BytesIO
# # import json
# # import tempfile
# # import psycopg2 

# # # # Define your database connection
# # # DATABASE_URL = "postgresql://username:password@localhost/genai"
# # # engine = create_engine(DATABASE_URL)


# # db_connection = {
# #     "host": "34.93.64.44",
# #     "port": "5432",
# #     "dbname": "genai",
# #     "user": "postgres",
# #     "password": "postgres-genai"
# # }

# # dialect = "postgresql"
# # host = "34.93.64.44"
# # port = "5432"
# # database = "genai"
# # username = "postgres"
# # password = "postgres-genai"

# # logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
# # logger = logging.getLogger()
# # conn= psycopg2.connect(**db_connection)
# # cursor= conn.cursor()
# # # Title of the page
# # st.title("Fine-tuning GenAI Project")

# # # Initialize session state variables
# # if "image_number" not in st.session_state:
# #     st.session_state.image_number = 1
# # if "navigation_clicked" not in st.session_state:
# #     st.session_state.navigation_clicked = False

# # # Load Google Cloud Storage credentials
# # gcs_credentials = json.loads(st.secrets["database"]["credentials"])
# # with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_file:
# #     json.dump(gcs_credentials, temp_file)
# #     temp_file_path = temp_file.name
# # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path
# # client = storage.Client()

# # # Specify your bucket name
# # bucket_name = 'open-to-public-rw-sairam'
# # bucket = client.get_bucket(bucket_name)

# # # Find the maximum image number in the bucket
# # def find_max_image_number(bucket, prefix):
# #     max_image_number = 0
# #     blobs = bucket.list_blobs(prefix=prefix)
# #     for blob in blobs:
# #         try:
# #             filename = os.path.basename(blob.name)
# #             if filename.startswith('image') and filename.endswith('.jpg'):
# #                 num = int(filename[5:-4])
# #                 max_image_number = max(max_image_number, num)
# #         except ValueError:
# #             continue
# #     return max_image_number

# # # Image prefix for storage
# # image_prefix = "Prompts/Final images moodboard/"
# # MAX_IMAGE_NUMBER = find_max_image_number(bucket, image_prefix)

# # # Connect to the PostgreSQL database
# # connection_string = st.secrets["database"]["connection_string"]
# # engine = create_engine(connection_string)

# # # Function to check if image exists in bucket
# # def image_exists_in_bucket(bucket, image_path):
# #     blob = bucket.blob(image_path)
# #     try:
# #         blob.reload()
# #         return True
# #     except Exception:
# #         return False

# # # Navigation callback functions
# # def go_back():
# #     if st.session_state.image_number > 1 and not st.session_state.navigation_clicked:
# #         st.session_state.image_number -= 1
# #         st.session_state.navigation_clicked = True

# # def go_next():
# #     if not st.session_state.navigation_clicked and st.session_state.image_number < MAX_IMAGE_NUMBER:
# #         st.session_state.image_number += 1
# #         st.session_state.navigation_clicked = True

# # # Function to fetch prompts from PostgreSQL based on image number
# # def get_prompts(image_number):
# #     query = f"""
# #     SELECT serial_nos, sno, image_prompts, 
# #            COALESCE(prompt_feedback, 10) AS prompt_feedback,
# #            COALESCE(status, 'PENDING') AS status
# #     FROM prompts
# #     WHERE sno = {image_number}
# #     ORDER BY serial_nos;
# #     """
# #     prompts_df = pd.read_sql(query, engine)
# #     return prompts_df

# # # Function to fetch image feedback and status
# # def get_image_feedback(image_name):
# #     query = text("""
# #     SELECT COALESCE(image_feedback, 10) AS image_feedback,
# #            COALESCE(status, 'PENDING') AS status
# #     FROM images
# #     WHERE image = :image_name
# #     """)
# #     with engine.connect() as conn:
# #         result = conn.execute(query, {"image_name": image_name}).fetchone()
# #     return result[0] if result else 10, result[1] if result else 'PENDING'

# # # Function to update prompt in the database
# # def update_prompt(serial_nos, new_prompt):
# #     try:
# #         serial_nos = int(serial_nos)
# #         logger.info(f"serialnos= {serial_nos}")
        
# #         # Log the data before the query to verify values
# #         # st.write(f"Updating prompt with serial_nos: {serial_nos}, prompt_feedback: {prompt_feedback}, image_prompts: {image_prompts}")
        
# #         # SQL Query to update the prompt and feedback in the database
# #         update_query = """
# #         UPDATE prompts
# #         SET image_prompts = %s 
# #         WHERE serial_nos = %s
# #         """
        
# #         # Log the query and the parameters being passed to verify
# #         st.write(f"Query: {update_query}")
# #         # st.write(f"Parameters: {serial_nos: {serial_nos}, prompt_feedback: {prompt_feedback}, image_prompts: {image_prompts}}")

# #         # Connect to the database and execute the update query
# #         # with engine.connect() as conn:
# #         result = conn.execute(update_query, (
# #             serial_nos, 
# #             new_prompt
# #         ))
# #         conn.commit()

# #         # Check if any rows were affected
# #         if result.rowcount > 0:
# #             st.success("Prompt updated successfully!")
# #         else:
# #             st.warning("No rows were updated. Check if the serial_nos exists in the database.")
        
# #     except Exception as e:
# #         # Log and show error if something goes wrong
# #         st.error(f"Failed to update prompt: {e}")

# # # Function to update image review
# # def update_image_review(image_name, review):
# #     try:
# #         update_query = text("""
# #         UPDATE images
# #         SET image_feedback = :review
# #         WHERE image = :image_name
# #         """)
# #         with engine.connect() as conn:
# #             conn.execute(update_query, {"review": review, "image_name": image_name})
# #             conn.commit()
# #         st.success("Image review updated successfully!")
# #     except Exception as e:
# #         st.error(f"Failed to update image review: {e}")

# # # Function to add new prompt
# # def add_new_prompt(image_number, prompt_text):
# #     try:
# #         insert_query = text("""
# #         INSERT INTO prompts (sno, image_prompts, prompt_feedback, status)
# #         VALUES (:sno, :prompt_text, 10, 'PENDING')
# #         """)
# #         with engine.connect() as conn:
# #             conn.execute(insert_query, {
# #                 "sno": image_number,
# #                 "prompt_text": prompt_text
# #             })
# #             conn.commit()
# #         st.success("New prompt added successfully!")
# #     except Exception as e:
# #         st.error(f"Failed to add new prompt: {e}")


# # # Function to handle image number update
# # def update_image_number():

   
# #     try:
# #         # Use the input from the text input to update image number
# #         input_number = int(st.session_state.image_number_input)
# #         if input_number < 1 or input_number > MAX_IMAGE_NUMBER:
# #             st.error(f"Please enter a number between 1 and {MAX_IMAGE_NUMBER}.")
# #         else:
# #             st.session_state.image_number = input_number
# #     except ValueError:
# #         st.error("Please enter a valid integer.")
        
# # col1, col2 , col3= st.columns([1, 2, 3])

# # with col1:
# #     st.markdown(f"<h3 style='text-align: center'>Image {st.session_state.image_number}</h3>", unsafe_allow_html=True)

# # with col3:     
# #         image_number_input = st.text_input(
# #         "Enter Image Number:", 
# #         value=str(st.session_state.image_number),
            
# #         key="image_number_input",
# #         on_change=update_image_number
# #         )

# # # # Valid
# # # Display the selected image and its prompts
# # image_name = f"image{st.session_state.image_number}.jpg"
# # image_path = os.path.join(image_prefix, image_name)

# # col1, col2 = st.columns([1, 2])

# # with col1:
# #     # Load the image from Google Cloud Storage
# #     try:
# #         if image_exists_in_bucket(bucket, image_path):
# #             blob = bucket.blob(image_path)
# #             image_data = blob.download_as_bytes()
# #             image = Image.open(BytesIO(image_data))
# #             st.image(image, caption=f"Image {st.session_state.image_number}")
# #         else:
# #             st.error(f"Image {st.session_state.image_number} not found.")
# #     except Exception as e:
# #         st.error(f"Error loading image: {e}")

# #     # Get existing review and status from the database
# #     image_review_score, image_status = get_image_feedback(image_name)

# #     # Image rating slider
# #     image_review = st.slider(f"Rate Image {st.session_state.image_number}:", 1, 10, value=image_review_score, format="%d")

# #     if st.button(f"Submit rating"):
# #         update_image_review(image_name, image_review)
        
# # with col2:
# #     prompts_df = get_prompts(st.session_state.image_number)
# #     if not prompts_df.empty:
# #         prompt_options = prompts_df['image_prompts'].tolist()
# #         selected_prompt_index = st.selectbox(f"Select Prompt for Image {st.session_state.image_number}", 
# #                                              range(len(prompt_options)), 
# #                                              format_func=lambda x: f"Prompt {x+1}")
# #         selected_prompt = prompt_options[selected_prompt_index]
# #         serial_nos = prompts_df.iloc[selected_prompt_index]['serial_nos']
# #         prompt_status = prompts_df.iloc[selected_prompt_index]['status']

# #         # Track if edit button was clicked
# #         edit_button_clicked = st.button("🖉 Edit Prompt", key=f"edit_prompt_{serial_nos}")

# #         if edit_button_clicked:
# #             # Display the text area with the current prompt text
# #             new_prompt = st.text_area(f"Edit Prompt {selected_prompt_index + 1}", 
# #                                       value=selected_prompt, 
# #                                       key=f"prompt_{serial_nos}")
# #             # Display the rating slider for feedback
# #             prompt_review_score = st.slider(f"Rate Prompt {selected_prompt_index + 1}:", 
# #                                       1, 10, 
# #                                       value=int(prompts_df.iloc[selected_prompt_index]['prompt_feedback']), 
# #                                       format="%d", 
# #                                       key=f"review_{serial_nos}")
            
# #             # When the save button is clicked, update the prompt
# #             save_button_clicked = st.button("Save", key=f"save_prompt_{serial_nos}")
# #             if save_button_clicked:
# #                 # Capture the updated prompt text and feedback
# #                 # prompt_review_score = st.slider(f"Rate Prompt {selected_prompt_index + 1}:", 
# #                 #                                 1, 10, 
# #                 #                                 value=int(prompts_df.iloc[selected_prompt_index]['prompt_feedback']), 
# #                 #                                 format="%d", 
# #                 #                                 key=f"review_{serial_nos}")
                
# #                 # Call the update function to save the new prompt and feedback
# #                 update_prompt(serial_nos, new_prompt, prompt_review_score)
                
# #                 # After saving, refresh the prompts to ensure the updated one is shown
            
# #                 st.experimental_rerun()  # Re-runs the script to show the updated prompt
# #             correlation_review_score= st.slider(f"Correlation feedback(Integer)",min_value=0, max_value=10, value=0, step=1)
# #         else:
# #             # Display the prompt without edit option
# #             st.write(f"Prompt {selected_prompt_index + 1}: {selected_prompt}")

# #     else:
# #         st.warning(f"No prompts found for image {st.session_state.image_number}.")

# #     # Add new prompt section
# #     st.write(f"Add a new prompt for Image {st.session_state.image_number}:")
# #     new_prompt_input = st.text_area(f"New Prompt for Image {st.session_state.image_number}", 
# #                                     key=f"new_prompt_{st.session_state.image_number}")
# #     if st.button(f"Add New Prompt for Image {st.session_state.image_number}"):
# #         add_new_prompt(st.session_state.image_number, new_prompt_input)

# # # Navigation buttons
# # col1, col2, col3 = st.columns([1, 1, 1])

# # with col1:
# #     if st.button("← Back", key="back_button", on_click=go_back):
# #         pass

# # # with col2:
# # #     st.markdown(f"<h3 style='text-align: center'>Image {st.session_state.image_number}</h3>", unsafe_allow_html=True)

# # with col3:
# #     if st.button("Next →", key="next_button", on_click=go_next):
# #         pass

# # # Reset navigation_clicked state at the end of the script
# # if st.session_state.navigation_clicked:
# #     st.session_state.navigation_clicked = False

# # # Approve/Reject buttons styling
# # button_styles = """
# #     <style>
# #         .stButton > button[kind="primary"] {
# #             background-color: #28a745;
# #             color: white;
# #             border: none;
# #             width: 100%;
# #             padding: 15px;
# #             font-size: 18px;
# #         }
        
# #         #reject_button button {
# #             background-color: #dc3545;
# #             color: white;
# #             border: none;
# #             width: 100%;
# #             padding: 15px;
# #             font-size: 18px;
# #         }
        
# #         .stButton > button[kind="secondary"] {
# #             background-color: #2f4f4f;
# #             color: white;
# #             border: none;
# #             width: 100%;
# #             padding: 15px;
# #             font-size: 18px;
# #         }
        
# #         /* Navigation buttons */
# #         .stButton > button {
# #             padding: 10px 20px;
# #             font-size: 16px;
# #         }
# #     </style>
# # """
# # st.markdown(button_styles, unsafe_allow_html=True)

# # # Approve/Reject buttons
# # col1, col2 = st.columns(2)

# # with col1:
# #     if st.button("✓ Approve", key="approve_button", type="primary"):
# #         st.success(f"Image {st.session_state.image_number} Approved.")
# #         try:
# #             # Update image status
# #             image_update_query = text("""
# #             UPDATE images
# #             SET status = 'APPROVED'
# #             WHERE image = :image_name
# #             """)
            
# #             # Update all prompts status for this image
# #             prompts_update_query = text("""
# #             UPDATE prompts
# #             SET status = 'APPROVED'
# #             WHERE sno = :image_number
# #             """)
            
# #             with engine.connect() as conn:
# #                 conn.execute(image_update_query, {"image_name": image_name})
# #                 conn.execute(prompts_update_query, {"image_number": st.session_state.image_number})
# #                 conn.commit()
# #             st.success("Image and associated prompts status updated to Approved in the database.")
# #         except Exception as e:
# #             st.error(f"Failed to update status to Approved: {e}")

# # with col2:
# #     if st.button("✕ Reject", key="reject_button", type="secondary"):
# #         st.warning(f"Image {st.session_state.image_number} Rejected.")
# #         try:
# #             # Update image status
# #             image_update_query = text("""
# #             UPDATE images
# #             SET status = 'REJECTED'
# #             WHERE image = :image_name
# #             """)
        
# #             # Update all prompts status for this image
# #             prompts_update_query = text("""
# #             UPDATE prompts
# #             SET status = 'REJECTED'
# #             WHERE sno = :image_number
# #             """)
            
# #             with engine.connect() as conn:
# #                 conn.execute(image_update_query, {"image_name": image_name})
# #                 conn.execute(prompts_update_query, {"image_number": st.session_state.image_number})
# #                 conn.commit()
# #             st.warning("Image and associated prompts status updated to Rejected in the database.")
# #         except Exception as e:
# #             st.error(f"Failed to update status to Rejected: {e}")


# import logging
# import streamlit as st
# import os
# from PIL import Image
# import pandas as pd
# from sqlalchemy import create_engine, text
# from google.cloud import storage
# from io import BytesIO
# import json
# import tempfile




# # # Define your database connection
# # DATABASE_URL = "postgresql://username:password@localhost/genai"
# # engine = create_engine(DATABASE_URL)

# import psycopg2 

# db_connection = {
#     "host": "34.93.64.44",
#     "port": "5432",
#     "dbname": "genai",
#     "user": "postgres",
#     "password": "postgres-genai"
# }

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
# logger = logging.getLogger()
# logger.info("logger")
# conn = psycopg2.connect(**db_connection)
# cursor = conn.cursor()
# logger.info("db_connection")


# # Title of the page
# st.title("Fine-tuning GenAI Project")


# # Initialize session state variables
# if "image_number" not in st.session_state:
#     st.session_state.image_number = 1
# if "navigation_clicked" not in st.session_state:
#     st.session_state.navigation_clicked = False

# # Load Google Cloud Storage credentials
# gcs_credentials = json.loads(st.secrets["database"]["credentials"])
# with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_file:
#     json.dump(gcs_credentials, temp_file)
#     temp_file_path = temp_file.name
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path
# client = storage.Client()

# # Specify your bucket name
# bucket_name = 'open-to-public-rw-sairam'
# bucket = client.get_bucket(bucket_name)

# # Find the maximum image number in the bucket
# def find_max_image_number(bucket, prefix):
#     max_image_number = 0
#     blobs = bucket.list_blobs(prefix=prefix)
#     for blob in blobs:
#         try:
#             filename = os.path.basename(blob.name)
#             if filename.startswith('image') and filename.endswith('.jpg'):
#                 num = int(filename[5:-4])
#                 max_image_number = max(max_image_number, num)
#         except ValueError:
#             continue
#     return max_image_number

# # Image prefix for storage
# image_prefix = "Prompts/Final images moodboard/"
# MAX_IMAGE_NUMBER = find_max_image_number(bucket, image_prefix)

# # Connect to the PostgreSQL database
# connection_string = st.secrets["database"]["connection_string"]
# engine = create_engine(connection_string)

# # Function to check if image exists in bucket
# def image_exists_in_bucket(bucket, image_path):
#     blob = bucket.blob(image_path)
#     try:
#         blob.reload()
#         return True
#     except Exception:
#         return False

# # Navigation callback functions
# def go_back():
#     if st.session_state.image_number > 1 and not st.session_state.navigation_clicked:
#         st.session_state.image_number -= 1
#         st.session_state.navigation_clicked = True

# def go_next():
#     if not st.session_state.navigation_clicked and st.session_state.image_number < MAX_IMAGE_NUMBER:
#         st.session_state.image_number += 1
#         st.session_state.navigation_clicked = True

# # Function to fetch prompts from PostgreSQL based on image number
# def get_prompts(image_number):
#     query = f"""
#     SELECT serial_nos, sno, image_prompts, 
#            COALESCE(prompt_feedback, 10) AS prompt_feedback,
#            COALESCE(status, 'PENDING') AS status
#     FROM prompts
#     WHERE sno = {image_number}
#     ORDER BY serial_nos;
#     """
#     prompts_df = pd.read_sql(query, engine)
#     return prompts_df

# # Function to fetch image feedback and status
# def get_prompt_feedback(image_name):
#     query = text("""
#     SELECT COALESCE(prompt_feedback, 10) AS prompt_feedback,
#            COALESCE(status, 'PENDING') AS status
#     FROM prompts
#     WHERE image_prompts = :image_name
#     """)
#     with engine.connect() as conn:
#         result = conn.execute(query, {"image_name": image_name}).fetchone()
#     return result[0] if result else 10, result[1] if result else 'PENDING'

# # Function to fetch image feedback and status
# def get_image_feedback(image_name):
#     query = text("""
#     SELECT COALESCE(image_feedback, 10) AS image_feedback,
#            COALESCE(status, 'PENDING') AS status
#     FROM images
#     WHERE image = :image_name
#     """)
#     with engine.connect() as conn:
#         result = conn.execute(query, {"image_name": image_name}).fetchone()
#     return result[0] if result else 10, result[1] if result else 'PENDING'


# # # # Function to fetch correlation feedback and status
# # def get_correlation_feedback(image_name):
# #     query = text("""
# #     SELECT COALESCE(correlation_feedback, 10) AS correlation_feedback,
# #            COALESCE(status, 'PENDING') AS status
# #     FROM prompts
# #     WHERE prompts = :image_name
# #     """)
# #     with engine.connect() as conn:
# #         result = conn.execute(query, {"image_name": image_name}).fetchone()
# #     return result[0] if result else 10, result[1] if result else 'PENDING'

# # Function to update prompt in the database
# def update_prompt(serial_nos, new_prompt):
#     try:
#         serial_nos = int(serial_nos)
#         logger.info(f"sno => {serial_nos}")
#         logger.info(f"new_prompts => {new_prompt}")
        

        
#         # Log the data before the query to verify values
#         # st.write(f"Updating prompt with serial_nos: {serial_nos}, prompt_feedback: {prompt_feedback}, image_prompts: {image_prompts}")
        
#         # SQL Query to update the prompt and feedback in the database
#         update_query = """
#         UPDATE prompts
#         SET image_prompts = %s
#         WHERE serial_nos = %s
#         """
#         logger.info(f"update_query => {update_query}")
        
        
#         # Log the query and the parameters being passed to verify
#         # st.write(f"Query: {update_query}")
#         # st.write(f"Parameters: {serial_nos: {serial_nos}, prompt_feedback: {prompt_feedback}, image_prompts: {image_prompts}}")

#         # Connect to the database and execute the update query
#         # with engine.connect() as conn:
        
#         ##### Execute the query
        
#         cursor.execute(update_query, (
             
#             # prompt_feedback, 
#             # image_prompts
#             new_prompt,
#             serial_nos
#         ))
#         conn.commit()
#         logger.info("updated")

#         # Check if any rows were affected
#         if cursor.rowcount > 0:
#             st.success("Prompt updated successfully!")
#             logger.info(f"Rows updated: {cursor.rowcount}")
#         else:
#             st.warning("No rows were updated. Check if the serial_nos exists in the database.")
#             logger.warning(f"Query executed, but no rows matched serial_nos: {serial_nos}")
            
#     except Exception as e:
#         # Log and show error if something goes wrong
#         st.error(f"Failed to update prompt: {e}")
#         logger.error(f"Exception occurred: {e}")
        
# # Function to update image review
# def update_image_review(image_name, review):
#     try:
#         update_query = text("""
#         UPDATE images
#         SET image_feedback = :review
#         WHERE image = :image_name
#         """)
#         with engine.connect() as conn:
#             conn.execute(update_query, {"review": review, "image_name": image_name})
#             conn.commit()
#         st.success("Image review updated successfully!")
#     except Exception as e:
#         st.error(f"Failed to update image review: {e}")
        
# # Function to update image review
# def update_prompt_review(image_name, review):
#     try:
#         update_query = text("""
#         UPDATE prompts
#         SET prompt_feedback = :review
#         WHERE image_prompts = :image_name
#         """)
#         with engine.connect() as conn:
#             conn.execute(update_query, {"review": review, "image_name": image_name})
#             conn.commit()
#         st.success("prompt review updated successfully!")
#     except Exception as e:
#         st.error(f"Failed to update prompt review: {e}")



# # Function to add new prompt
# def add_new_prompt(image_number, prompt_text):
#     try:
#         insert_query = text("""
#         INSERT INTO prompts (sno, image_prompts, prompt_feedback, status)
#         VALUES (:sno, :prompt_text, 10, 'PENDING')
#         """)
#         with engine.connect() as conn:
#             conn.execute(insert_query, {
#                 "sno": image_number,
#                 "prompt_text": prompt_text
#             })
#             conn.commit()
#         st.success("New prompt added successfully!")
#     except Exception as e:
#         st.error(f"Failed to add new prompt: {e}")




# # Function to handle image number update
# def update_image_number():

   
#     try:
#         # Use the input from the text input to update image number
#         input_number = int(st.session_state.image_number_input)
#         if input_number < 1 or input_number > MAX_IMAGE_NUMBER:
#             st.error(f"Please enter a number between 1 and {MAX_IMAGE_NUMBER}.")
#         else:
#             st.session_state.image_number = input_number
#     except ValueError:
#         st.error("Please enter a valid integer.")
        
# col1, col2 , col3= st.columns([1, 2, 3])

# with col1:
#     st.markdown(f"<h3 style='text-align: center'>Image {st.session_state.image_number}</h3>", unsafe_allow_html=True)

# with col3:     
#         image_number_input = st.text_input(
#         "Enter Image Number:", 
#         value=str(st.session_state.image_number),
            
#         key="image_number_input",
#         on_change=update_image_number
#         )

# # # Valid
# # Display the selected image and its prompts
# image_name = f"image{st.session_state.image_number}.jpg"
# image_path = os.path.join(image_prefix, image_name)

# col1, col2 = st.columns([1, 2])

# with col1:
#     # Load the image from Google Cloud Storage
#     try:
#         if image_exists_in_bucket(bucket, image_path):
#             blob = bucket.blob(image_path)
#             image_data = blob.download_as_bytes()
#             image = Image.open(BytesIO(image_data))
#             st.image(image, caption=f"Image {st.session_state.image_number}")
#         else:
#             st.error(f"Image {st.session_state.image_number} not found.")
#     except Exception as e:
#         st.error(f"Error loading image: {e}")

#     # Get existing review and status from the database
#     image_review_score, image_status = get_image_feedback(image_name)

#     # Image rating slider
#     image_review = st.slider(f"Rate Image {st.session_state.image_number}:", 1, 10, value=image_review_score, format="%d")

#     if st.button(f"Submit rating"):
#         update_image_review(image_name, image_review)
        
# def on_text_change(serial_nos):
#     updated_value = st.session_state[f"prompt_{serial_nos}"]
#     logger.info(f"Edited value in on_text_change: {updated_value}")
#     st.session_state[f"new_prompt_{serial_nos}"] = updated_value
#     logger.info("Text area change processed.")


# with col2:
#     prompts_df = get_prompts(st.session_state.image_number)
#     if not prompts_df.empty:
#         prompt_options = prompts_df['image_prompts'].tolist()
#         selected_prompt_index = st.selectbox(
#             f"Select prompt for image {st.session_state.image_number}",
#             range(len(prompt_options)),
#             format_func=lambda x: f"Prompt {x + 1}"
#         )
#         selected_prompt = prompt_options[selected_prompt_index]
#         serial_nos = prompts_df.iloc[selected_prompt_index]['serial_nos']
        
#         # prompt_review_score = st.slider(f"Rate Prompt", 
#         #                               1, 10, 
#         #                               value=0, 
#         #                               format="%d", 
#         #                               key=f"review_{serial_nos}")
        
#         # if st.button(f"Submit prompt"):
#         #  get_prompt_review(image_name, prompt_review_score)
        
#         # Get existing review and status from the database
#         # image_review_score, image_status = get_prompt_feedback(image_name)
#         # # prompt_status = prompts_df.iloc[selected_prompt_idex]['status']
#         # prompt_review= st.slider(f"prompt_review(Integer)", min_value=1, max_value=10, value=0, step =1)
#         # Initialize session state variables
#         if "edit_mode" not in st.session_state:
#             st.session_state.edit_mode = False
#         if "update_prompt" not in st.session_state:
#             st.session_state.update_prompt = False
        
#     # Get existing review and status from the database
#         prompt_review_score, image_status = get_prompt_feedback(image_name)

#     # Image rating slider
#         # prompt_review = st.slider(f"Rate Image {st.session_state.image_number}:", 1, 10, value=0, format="%d")
        
#         prompt_review_score = st.slider(f"Rate Prompt {selected_prompt_index + 1}:", 
#                                         1, 10, 
#                                         value=int(prompts_df.iloc[selected_prompt_index]['prompt_feedback']), 
#                                         format="%d", 
#                                         key=f"review_{serial_nos}")
# # col1, col2, col3 = st.columns([1, 2, 3])
# # with col3:
#         # if st.button(f"Save Prompt {selected_prompt_index + 1}", key=f"save_prompt_{serial_nos}"):
#         #     update_prompt(serial_nos, new_prompt, prompt_review_score)
#         if st.button(f"prompt rating"):
#           update_prompt_review(serial_nos, prompt_review_score)
#         # Edit Prompt Button
#         if st.button("🖉 Edit Prompt", key=f"edit_prompt_{serial_nos}"):
#             st.text_area(selected_prompt)
#             st.session_state.edit_mode = True
#             st.session_state.update_prompt = False  # Reset update state for fresh edit
#             logger.info("Edit mode activated.")
        
#         # Edit Mode Section
#             if st.session_state.edit_mode:
#                 st.text_area(
#                     f"Edit prompt {selected_prompt_index + 1}",
#                     value=selected_prompt,
#                     key=f"prompt_{serial_nos}",
#                     on_change=lambda: on_text_change(serial_nos)
#                 )
#                 st.session_state.update_prompt = True
#                 logger.info("Ready to update prompt.")

#             # Update Prompt Section
#         if st.session_state.update_prompt:
#             logger.info("Update button active.")
#             # logger.info(st.button("Update Prompt"))
#             if st.button("Update Prompt", key=f"update_prompt_{serial_nos}"):
#                 logger.info("Update button clicked.")
#                 new_prompt_value = st.session_state.get(f"new_prompt_{serial_nos}")
#                 logger.info(f"New prompt value: {new_prompt_value}")
#                 if new_prompt_value:
#                     update_prompt(serial_nos, new_prompt_value)
#                     st.session_state.edit_mode = False  # Reset edit mode
#                     st.session_state.update_prompt = False  # Reset update state
#                     logger.info(f"Prompt {serial_nos} successfully updated.")
#                 else:
#                     logger.warning("No new prompt value provided.")
#             # st.experimental_rerun()

#         # logger.info(f"prompt_options => {prompt_options}")
#         # selected_prompt_index = st.selectbox(f"Select Prompt for Image {st.session_state.image_number}",
#         #                                      range(len(prompt_options)),
#         #                                      format_func=lambda x: f"Prompt {x+1}")
#         # logger.info(f"selected_prompt_index => {selected_prompt_index}")
#         # selected_prompt = prompt_options[selected_prompt_index]
#         # logger.info(f"selected_prompt => {selected_prompt}")
#         # serial_nos = prompts_df.iloc[selected_prompt_index]['serial_nos']
#         # logger.info(f"serial_nos => {serial_nos}")
#         # prompt_status = prompts_df.iloc[selected_prompt_index]['status']
#         # logger.info(f"prompt_status => {prompt_status}")

#         # # Track if edit button was clicked
#         # edit_button_clicked = st.button("🖉 Edit Prompt", key=f"edit_prompt_{serial_nos}")

#         # if edit_button_clicked:
#         #     # Display the text area with the current prompt text
#         #     new_prompt = st.text_area(f"Edit Prompt {selected_prompt_index + 1}", 
#         #                               value=selected_prompt, 
#         #                               key=f"prompt_{serial_nos}")
#         #     prompts_update = st.button("update_prompt")
#         #     logger.info("button this clicked")
#         #     logger.info(f"new_prompt => {new_prompt}")
#         #     logger.info(prompts_update)
#         #     # st.session_state("update_prompt") == prompts_update

#         #     # Display the rating slider for feedback
#         #     prompt_review_score = st.slider(f"Rate Prompt {selected_prompt_index + 1}:", 
#         #                               1, 10, 
#         #                               value=int(prompts_df.iloc[selected_prompt_index]['prompt_feedback']), 
#         #                               format="%d", 
#         #                               key=f"review_{serial_nos}")
            
#         #     # When the save button is clicked, update the prompt
#         #     save_button_clicked = st.button("Save", key=f"save_prompt_{serial_nos}")
#         #     if save_button_clicked:
#         #         # Capture the updated prompt text and feedback
#         #         # prompt_review_score = st.slider(f"Rate Prompt {selected_prompt_index + 1}:", 
#         #         #                                 1, 10, 
#         #         #                                 value=int(prompts_df.iloc[selected_prompt_index]['prompt_feedback']), 
#         #         #                                 format="%d", 
#         #         #                                 key=f"review_{serial_nos}")
                
#         #         # Call the update function to save the new prompt and feedback
#         #         update_prompt(serial_nos, new_prompt, prompt_review_score)

#         #     if prompts_update:
#         #         logger.info(f"prompts_update = {prompts_update}")
#         #         update_prompt(serial_nos,new_prompt)
    

                
#                 # After saving, refresh the prompts to ensure the updated one is shown
            
#         #     st.experimental_rerun()  # Re-runs the script to show the updated prompt
#         #     correlation_review_score= st.slider(f"Correlation feedback(Integer)",min_value=0, max_value=10, value=0, step=1)
#         # else:
#         #     # Display the prompt without edit option
#         #     st.write(f"Prompt {selected_prompt_index + 1}: {selected_prompt}")

#     else:
#         st.warning(f"No prompts found for image {st.session_state.image_number}.")
    
#     # # Get existing review and status from the database
#     # image_review_score, image_status = get_correlation_feedback(image_name)
#     # correlation_review_score = st.slider(f"Correlation_feedback(Integer)",min_value=1, max_value=10, value=0, step=1)

#     # Add new prompt section
#     st.write(f"Add a new prompt for Image {st.session_state.image_number}:")
#     new_prompt_input = st.text_area(f"New Prompt for Image {st.session_state.image_number}", 
#                                     key=f"new_prompt_{st.session_state.image_number}")
#     if st.button(f"Add New Prompt for Image {st.session_state.image_number}"):
#         add_new_prompt(st.session_state.image_number, new_prompt_input)
        

# # Navigation buttons
# col1, col2, col3 = st.columns([1, 1, 1])

# with col1:
#     if st.button("← Back", key="back_button", on_click=go_back):
#         pass

# # with col2:
# #     st.markdown(f"<h3 style='text-align: center'>Image {st.session_state.image_number}</h3>", unsafe_allow_html=True)

# with col3:
#     if st.button("Next →", key="next_button", on_click=go_next):
#         pass

# # Reset navigation_clicked state at the end of the script
# if st.session_state.navigation_clicked:
#     st.session_state.navigation_clicked = False

# # Approve/Reject buttons styling
# button_styles = """
#     <style>
#         .stButton > button[kind="primary"] {
#             background-color: #28a745;
#             color: white;
#             border: none;
#             width: 100%;
#             padding: 15px;
#             font-size: 18px;
#         }
        
#         #reject_button button {
#             background-color: #dc3545;
#             color: white;
#             border: none;
#             width: 100%;
#             padding: 15px;
#             font-size: 18px;
#         }
        
#         .stButton > button[kind="secondary"] {
#             background-color: #2f4f4f;
#             color: white;
#             border: none;
#             width: 100%;
#             padding: 15px;
#             font-size: 18px;
#         }
        
#         /* Navigation buttons */
#         .stButton > button {
#             padding: 10px 20px;
#             font-size: 16px;
#         }
#     </style>
# """
# st.markdown(button_styles, unsafe_allow_html=True)

# # Approve/Reject buttons
# col1, col2 = st.columns(2)

# with col1:
#     if st.button("✓ Approve", key="approve_button", type="primary"):
#         st.success(f"Image {st.session_state.image_number} Approved.")
#         try:
#             # Update image status
#             image_update_query = text("""
#             UPDATE images
#             SET status = 'APPROVED'
#             WHERE image = :image_name
#             """)
            
#             # Update all prompts status for this image
#             prompts_update_query = text("""
#             UPDATE prompts
#             SET status = 'APPROVED'
#             WHERE sno = :image_number
#             """)
            
#             with engine.connect() as conn:
#                 conn.execute(image_update_query, {"image_name": image_name})
#                 conn.execute(prompts_update_query, {"image_number": st.session_state.image_number})
#                 conn.commit()
#             st.success("Image and associated prompts status updated to Approved in the database.")
#         except Exception as e:
#             st.error(f"Failed to update status to Approved: {e}")

# with col2:
#     if st.button("✕ Reject", key="reject_button", type="secondary"):
#         st.warning(f"Image {st.session_state.image_number} Rejected.")
#         try:
#             # Update image status
#             image_update_query = text("""
#             UPDATE images
#             SET status = 'REJECTED'
#             WHERE image = :image_name
#             """)
            
#             # Update all prompts status for this image
#             prompts_update_query = text("""
#             UPDATE prompts
#             SET status = 'REJECTED'
#             WHERE sno = :image_number
#             """)
            
#             with engine.connect() as conn:
#                 conn.execute(image_update_query, {"image_name": image_name})
#                 conn.execute(prompts_update_query, {"image_number": st.session_state.image_number})
#                 conn.commit()
#             st.warning("Image and associated prompts status updated to Rejected in the database.")
#         except Exception as e:
#             st.error(f"Failed to update status to Rejected: {e}")



import logging
import streamlit as st
import os
from PIL import Image
import pandas as pd
from sqlalchemy import create_engine, text
from google.cloud import storage
from io import BytesIO
import json
import tempfile




# # Define your database connection
# DATABASE_URL = "postgresql://username:password@localhost/genai"
# engine = create_engine(DATABASE_URL)

import psycopg2 

db_connection = {
    "host": "34.93.64.44",
    "port": "5432",
    "dbname": "genai",
    "user": "postgres",
    "password": "postgres-genai"
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()
logger.info("logger")
conn = psycopg2.connect(**db_connection)
cursor = conn.cursor()
logger.info("db_connection")


# Title of the page
st.title("Fine-tuning GenAI Project")


# Initialize session state variables
if "image_number" not in st.session_state:
    st.session_state.image_number = 1
if "navigation_clicked" not in st.session_state:
    st.session_state.navigation_clicked = False

# Load Google Cloud Storage credentials
gcs_credentials = json.loads(st.secrets["database"]["credentials"])
with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as temp_file:
    json.dump(gcs_credentials, temp_file)
    temp_file_path = temp_file.name
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path
client = storage.Client()

# Specify your bucket name
bucket_name = 'open-to-public-rw-sairam'
bucket = client.get_bucket(bucket_name)

# Find the maximum image number in the bucket
def find_max_image_number(bucket, prefix):
    max_image_number = 0
    blobs = bucket.list_blobs(prefix=prefix)
    for blob in blobs:
        try:
            filename = os.path.basename(blob.name)
            if filename.startswith('image') and filename.endswith('.jpg'):
                num = int(filename[5:-4])
                max_image_number = max(max_image_number, num)
        except ValueError:
            continue
    return max_image_number

# Image prefix for storage
image_prefix = "Prompts/Final images moodboard/"
MAX_IMAGE_NUMBER = find_max_image_number(bucket, image_prefix)

# Connect to the PostgreSQL database
connection_string = st.secrets["database"]["connection_string"]
engine = create_engine(connection_string)

# Function to check if image exists in bucket
def image_exists_in_bucket(bucket, image_path):
    blob = bucket.blob(image_path)
    try:
        blob.reload()
        return True
    except Exception:
        return False

# Navigation callback functions
def go_back():
    if st.session_state.image_number > 1 and not st.session_state.navigation_clicked:
        st.session_state.image_number -= 1
        st.session_state.navigation_clicked = True

def go_next():
    if not st.session_state.navigation_clicked and st.session_state.image_number < MAX_IMAGE_NUMBER:
        st.session_state.image_number += 1
        st.session_state.navigation_clicked = True

# Function to fetch prompts from PostgreSQL based on image number
def get_prompts(image_number):
    query = f"""
    SELECT serial_nos, sno, image_prompts, 
           COALESCE(prompt_feedback, 10) AS prompt_feedback,
           COALESCE(status, 'PENDING') AS status
    FROM prompts
    WHERE sno = {image_number}
    ORDER BY serial_nos;
    """
    prompts_df = pd.read_sql(query, engine)
    return prompts_df

# Function to fetch image feedback and status
def get_prompt_feedback(image_name):
    query = text("""
    SELECT COALESCE(prompt_feedback, 10) AS prompt_feedback,
           COALESCE(status, 'PENDING') AS status
    FROM prompts
    WHERE image_prompts = :image_name
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"image_name": image_name}).fetchone()
    return result[0] if result else 10, result[1] if result else 'PENDING'

# Function to fetch image feedback and status
def get_image_feedback(image_name):
    query = text("""
    SELECT COALESCE(image_feedback, 10) AS image_feedback,
           COALESCE(status, 'PENDING') AS status
    FROM images
    WHERE image = :image_name
    """)
    with engine.connect() as conn:
        result = conn.execute(query,{"image_name": image_name}).fetchone()
    return result[0] if result else 10, result[1] if result else 'PENDING'


# # # Function to fetch correlation feedback and status
# def get_correlation_feedback(image_name):
#     query = text("""
#     SELECT COALESCE(correlation_feedback, 10) AS correlation_feedback,
#            COALESCE(status, 'PENDING') AS status
#     FROM prompts
#     WHERE prompts = :image_name
#     """)
#     with engine.connect() as conn:
#         result = conn.execute(query, {"image_name": image_name}).fetchone()
#     return result[0] if result else 10, result[1] if result else 'PENDING'

# Function to update prompt in the database
def update_prompt(serial_nos, new_prompt):
    try:
        serial_nos = int(serial_nos)
        logger.info(f"sno => {serial_nos}")
        logger.info(f"new_prompts => {new_prompt}")
        

        
        # Log the data before the query to verify values
        # st.write(f"Updating prompt with serial_nos: {serial_nos}, prompt_feedback: {prompt_feedback}, image_prompts: {image_prompts}")
        
        # SQL Query to update the prompt and feedback in the database
        update_query = """
        UPDATE prompts
        SET image_prompts = %s
        WHERE serial_nos = %s
        """
        logger.info(f"update_query => {update_query}")
        
        
        # Log the query and the parameters being passed to verify
        # st.write(f"Query: {update_query}")
        # st.write(f"Parameters: {serial_nos: {serial_nos}, prompt_feedback: {prompt_feedback}, image_prompts: {image_prompts}}")

        # Connect to the database and execute the update query
        # with engine.connect() as conn:
        
        ##### Execute the query
        
        cursor.execute(update_query, (
             
            # prompt_feedback, 
            # image_prompts
            new_prompt,
            serial_nos
        ))
        conn.commit()
        logger.info("updated")

        # Check if any rows were affected
        if cursor.rowcount > 0:
            st.success("Prompt updated successfully!")
            logger.info(f"Rows updated: {cursor.rowcount}")
        else:
            st.warning("No rows were updated. Check if the serial_nos exists in the database.")
            logger.warning(f"Query executed, but no rows matched serial_nos: {serial_nos}")
            
    except Exception as e:
        # Log and show error if something goes wrong
        st.error(f"Failed to update prompt: {e}")
        logger.error(f"Exception occurred: {e}")
       
# Function to update image review
def update_image_review(image_name, review):
    logger.info(image_name)
    logger.info(review)
    try:
        update_query = """
        UPDATE images
        SET image_feedback = %s
        WHERE image = %s
        """
        logger.info(update_query)
        # with engine.connect() as conn:
        cursor.execute(update_query,(review, image_name))
        conn.commit()
        st.success("Image review updated successfully!")
    except Exception as e:
        st.error(f"Failed to update image review: {e}")
        
# Function to update image review
def update_prompt_review(serial_nos, review):
    logger.info("entering")
    try:
        update_query = """
        UPDATE prompts
        SET prompt_feedback = %s
        WHERE serial_nos = %s
        """
        
        # with engine.connect() as conn:
        cursor.execute(update_query, (review, int(serial_nos)))
        conn.commit()
        st.success("prompt review updated successfully!")
    except Exception as e:
        st.error(f"Failed to update prompt review: {e}")
        
def update_corelation_review(serial_nos, corelation_review):
    logger.info("entering")
    try:
        update_query = """
        UPDATE prompts
        SET correlation_feedback = %s
        WHERE serial_nos = %s
        """
        
        # with engine.connect() as conn:
        cursor.execute(update_query, (corelation_review, int(serial_nos)))
        conn.commit()
        st.success("correlation review updated successfully!")
    except Exception as e:
        st.error(f"Failed to update correlation review: {e}")



# Function to add new prompt
def add_new_prompt(image_number, prompt_text):
    try:
        insert_query = text("""
        INSERT INTO prompts (sno, image_prompts, prompt_feedback, status)
        VALUES (:sno, :prompt_text, 10, 'PENDING')
        """)
        with engine.connect() as conn:
            conn.execute(insert_query, {
                "sno": image_number,
                "prompt_text": prompt_text
            })
            conn.commit()
        st.success("New prompt added successfully!")
    except Exception as e:
        st.error(f"Failed to add new prompt: {e}")


# Function to handle image number update
def update_image_number():

    try:
        # Use the input from the text input to update image number
        input_number = int(st.session_state.image_number_input)
        if input_number < 1 or input_number > MAX_IMAGE_NUMBER:
            st.error(f"Please enter a number between 1 and {MAX_IMAGE_NUMBER}.")
        else:
            st.session_state.image_number = input_number
    except ValueError:
        st.error("Please enter a valid integer.")
        
col1, col2 , col3= st.columns([1, 2, 3])

with col1:
    st.markdown(f"<h3 style='text-align: center'>Image {st.session_state.image_number}</h3>", unsafe_allow_html=True)

with col3:     
        image_number_input = st.text_input(
        "Enter Image Number:", 
        value=str(st.session_state.image_number),
            
        key="image_number_input",
        on_change=update_image_number
        )

# # Valid
# Display the selected image and its prompts
image_name = f"image{st.session_state.image_number}.jpg"
image_path = os.path.join(image_prefix, image_name)

col1, col2 = st.columns([1, 2])

with col1:
    # Load the image from Google Cloud Storage
    try:
        if image_exists_in_bucket(bucket, image_path):
            blob = bucket.blob(image_path)
            image_data = blob.download_as_bytes()
            image = Image.open(BytesIO(image_data))
            st.image(image, caption=f"Image {st.session_state.image_number}")
        else:
            st.error(f"Image {st.session_state.image_number} not found.")
    except Exception as e:
        st.error(f"Error loading image: {e}")

    # Get existing review and status from the database
    image_review_score, image_status = get_image_feedback(image_name)

    # Image rating slider
    image_review = st.slider(f"Rate Image {st.session_state.image_number}:", 1, 10, value=image_review_score, format="%d")

    if st.button(f"Submit rating"):
        update_image_review(image_name, image_review)


with col2:
    prompts_df = get_prompts(st.session_state.image_number)
    if not prompts_df.empty:
        prompt_options = prompts_df['image_prompts'].tolist()
        selected_prompt_index = st.selectbox(
            f"Select prompt for image {st.session_state.image_number}",
            range(len(prompt_options)),
            format_func=lambda x: f"Prompt {x + 1}"
        )
        selected_prompt = prompt_options[selected_prompt_index]
        serial_nos = prompts_df.iloc[selected_prompt_index]['serial_nos']
        
        
    # Get existing review and status from the database
        prompt_review_score, image_status = get_prompt_feedback(image_name)

    # Image rating slider
        st.write(f"Prompt:- {selected_prompt}")
        prompt_review = st.slider(f"Rate Prompt:", 1, 10, value=0, format="%d")

        if st.button(f"prompt rating"):
            update_prompt_review(serial_nos, prompt_review)
        # Edit Prompt Button
        if st.button("🖉 Edit Prompt", key=f"edit_prompt_{serial_nos}"):
            st.session_state.edit_mode = True
        
        if st.session_state.get("edit_mode"):
            with st.form(key=f"edit_form_{serial_nos}"):
                new_prompt = st.text_area(
                    f"Edit prompt {selected_prompt_index + 1}",
                    value=selected_prompt,
                    key=f"new_prompt_{serial_nos}"
                )
                submitted = st.form_submit_button("Update Prompt")
                if submitted:
                    logger.info("Update button clicked.")
                    if new_prompt:
                        update_prompt(serial_nos, new_prompt)
                        st.session_state.edit_mode = False  # Exit edit mode
                        logger.info(f"Prompt {serial_nos} successfully updated.")
                    else:
                        st.warning("Please provide a new prompt value.")
                        
        corelation_review = st.slider(f"Rate Correlation:", 1, 10, value=0, format="%d")

        if st.button(f"correlation rating submit"):
            update_corelation_review(serial_nos, corelation_review)
            # st.experimental_rerun()


    else:
        st.warning(f"No prompts found for image {st.session_state.image_number}.")
    
    # # Get existing review and status from the database
    # image_review_score, image_status = get_correlation_feedback(image_name)
    # correlation_review_score = st.slider(f"Correlation_feedback(Integer)",min_value=1, max_value=10, value=0, step=1)

    # Add new prompt section
    st.write(f"Add a new prompt for Image {st.session_state.image_number}:")
    new_prompt_input = st.text_area(f"New Prompt for Image {st.session_state.image_number}", 
                                    key=f"new_prompts_{st.session_state.image_number}")
    if st.button(f"Add New Prompt for Image {st.session_state.image_number}"):
        add_new_prompt(st.session_state.image_number, new_prompt_input)
        

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("← Back", key="back_button", on_click=go_back):
        pass

# with col2:
#     st.markdown(f"<h3 style='text-align: center'>Image {st.session_state.image_number}</h3>", unsafe_allow_html=True)

with col3:
    if st.button("Next →", key="next_button", on_click=go_next):
        pass

# Reset navigation_clicked state at the end of the script
if st.session_state.navigation_clicked:
    st.session_state.navigation_clicked = False

# Approve/Reject buttons styling
button_styles = """
    <style>
        .stButton > button[kind="primary"] {
            background-color: #28a745;
            color: white;
            border: none;
            width: 100%;
            padding: 15px;
            font-size: 18px;
        }
        
        #reject_button button {
            background-color: #dc3545;
            color: white;
            border: none;
            width: 100%;
            padding: 15px;
            font-size: 18px;
        }
        
        .stButton > button[kind="secondary"] {
            background-color: #2f4f4f;
            color: white;
            border: none;
            width: 100%;
            padding: 15px;
            font-size: 18px;
        }
        
        /* Navigation buttons */
        .stButton > button {
            padding: 10px 20px;
            font-size: 16px;
        }
    </style>
"""
st.markdown(button_styles, unsafe_allow_html=True)

# Approve/Reject buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("✓ Approve", key="approve_button", type="primary"):
        st.success(f"Image {st.session_state.image_number} Approved.")
        try:
            # Update image status
            image_update_query = text("""
            UPDATE images
            SET status = 'APPROVED'
            WHERE image = :image_name
            """)
            
            # Update all prompts status for this image
            prompts_update_query = text("""
            UPDATE prompts
            SET status = 'APPROVED'
            WHERE sno = :image_number
            """)
            
            with engine.connect() as conn:
                conn.execute(image_update_query, {"image_name": image_name})
                conn.execute(prompts_update_query, {"image_number": st.session_state.image_number})
                conn.commit()
            st.success("Image and associated prompts status updated to Approved in the database.")
        except Exception as e:
            st.error(f"Failed to update status to Approved: {e}")

with col2:
    if st.button("✕ Reject", key="reject_button", type="secondary"):
        st.warning(f"Image {st.session_state.image_number} Rejected.")
        try:
            # Update image status
            image_update_query = text("""
            UPDATE images
            SET status = 'REJECTED'
            WHERE image = :image_name
            """)
            
            # Update all prompts status for this image
            prompts_update_query = text("""
            UPDATE prompts
            SET status = 'REJECTED'
            WHERE sno = :image_number
            """)
            
            with engine.connect() as conn:
                conn.execute(image_update_query, {"image_name": image_name})
                conn.execute(prompts_update_query, {"image_number": st.session_state.image_number})
                conn.commit()
            st.warning("Image and associated prompts status updated to Rejected in the database.")
        except Exception as e:
            st.error(f"Failed to update status to Rejected: {e}")

