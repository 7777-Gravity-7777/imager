import streamlit as st
import requests
import urllib.parse
import google.generativeai as genai
import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
from gradio_client import Client, handle_file
#test
# Set up the page configuration for title and favicon
st.set_page_config(page_title="Imager", page_icon="✨", layout="wide")

# Set up the API key for Google Gemini (should be securely managed in practice)
api_key = 'AIzaSyDDmIfcyTt3r5sCsid0BrCHiURJawVHdkY'  # Replace with your actual Google Gemini API key
os.environ["API_KEY"] = api_key
genai.configure(api_key=api_key)

# Define the system instruction for Google Gemini for enhanced prompts
instruction = """
You are an AI expert specializing in the creation of unique, high-quality image prompts. Your task is to transform a basic user-provided image description into a highly detailed, visually captivating prompt that will produce stunning, high-resolution images. Focus on enriching the description with elements that enhance the visual depth, including:

Lighting: Specify the type of lighting (e.g., soft, dramatic, natural, studio), the direction (e.g., side-lit, backlit, overhead), and the quality (e.g., diffused, harsh, warm, cool) to evoke the desired mood and atmosphere.

Textures: Include rich, descriptive textures such as the roughness of stone, the softness of fabric, the glossiness of metal, or the smoothness of water, ensuring the material qualities are clear and contribute to the overall feel of the scene.

Composition: Consider the balance, focal points, and framing of the image. Describe how elements are arranged, from the foreground to the background, and any dynamic contrasts (e.g., close-ups, wide shots, rule of thirds, leading lines).

Color Schemes: Detail specific color palettes to evoke emotion or harmony (e.g., pastel hues for a calm scene, bold contrasts for energy, monochrome for a dramatic look). You can also note how colors interact in different parts of the image.

Atmosphere & Mood: Indicate the emotional tone of the image—whether serene, tense, joyful, mysterious—and how the scene's elements, like weather (e.g., fog, rain, sunlight) or time of day (e.g., golden hour, twilight), contribute to this mood."""

# Function to generate enhanced image prompts using Google Gemini API
gradio_client = Client("DamarJati/Remove-watermark")

def remove_watermark(image_path):
    """Uses the Gradio client to remove watermarks from the image."""
    try:
        result = gradio_client.predict(
            image=handle_file(image_path),
            model_choice="microsoft/Florence-2-large",
            api_name="/predict"
        )
        return result
    except Exception as e:
        return f"Error in watermark removal: {str(e)}"

def enhance_image(image_url, upscale_factor=2, seed=42,prompta):
    """Enhances the image using Finegrain Image Enhancer."""
    client = Client("finegrain/finegrain-image-enhancer")
    try:
        result = client.predict(
            input_image=handle_file(image_url),
            prompta="""Upscale the image to ultra-high resolution while maintaining the integrity of the original composition and preserving sharpness in all 
            key elements. 
            Focus on enhancing fine details, such as textures, edges, and small features that might lose clarity during the enlargement process. 
            Sharpen and define intricate details, especially in areas like skin, fabric, or metal, ensuring they are crisp and clear. Improve the overall 
            vibrancy of the colors, making sure they remain natural but enhanced, with rich, warm tones and smooth gradients. Reduce any noise or 
            pixelation that might appear as a result of upscaling, ensuring the image stays clean and free of artifacts. Enhance textures such as fabric, 
            stone, and water, ensuring their qualities (smoothness, roughness, glossiness) are clearly visible and realistic. Maintain the original mood and 
            style of the image, applying any artistic effects subtly without altering the fundamental appearance. Finally, ensure the image is optimized for 
            display on large screens or high-quality prints, with all details clear and lifelike, 
            ensuring no blurring or loss of quality.""",
            negative_prompt="Hello!!",
            seed=seed,
            upscale_factor=upscale_factor,
            controlnet_scale=0.6,
            controlnet_decay=1,
            condition_scale=6,
            tile_width=112,
            tile_height=144,
            denoise_strength=0.35,
            num_inference_steps=18,
            solver="DDIM",
            api_name="/process"
        )
        return result
    except Exception as e:
        return f"Error in image enhancement: {str(e)}"
    
def generate_enhanced_prompt(basic_prompt):
    prompt = f"""Basic prompt: {basic_prompt}.  You are an AI expert specializing in the creation of unique, high-quality image prompts. Your task is to transform a basic user-provided image description into a highly detailed, visually captivating prompt that will produce stunning, high-resolution images. Focus on enriching the description with elements that enhance the visual depth, including:

Lighting: Specify the type of lighting (e.g., soft, dramatic, natural, studio), the direction (e.g., side-lit, backlit, overhead), and the quality (e.g., diffused, harsh, warm, cool) to evoke the desired mood and atmosphere.

Textures: Include rich, descriptive textures such as the roughness of stone, the softness of fabric, the glossiness of metal, or the smoothness of water, ensuring the material qualities are clear and contribute to the overall feel of the scene.

Composition: Consider the balance, focal points, and framing of the image. Describe how elements are arranged, from the foreground to the background, and any dynamic contrasts (e.g., close-ups, wide shots, rule of thirds, leading lines).

Color Schemes: Detail specific color palettes to evoke emotion or harmony (e.g., pastel hues for a calm scene, bold contrasts for energy, monochrome for a dramatic look). You can also note how colors interact in different parts of the image.

Atmosphere & Mood: Indicate the emotional tone of the image—whether serene, tense, joyful, mysterious—and how the scene's elements, like weather (e.g., fog, rain, sunlight) or time of day (e.g., golden hour, twilight), contribute to this mood."""

    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel("gemini-1.5-flash-latest", system_instruction=instruction, 
                                
                                      safety_settings={
                                          HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
                                          HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,  
                                          HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, 
                                          HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
                                          
        }
    )
        # Start a chat with the model
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        
        # Return the enriched prompt text generated by Gemini, stripping any extra details
        enhanced_prompt = response.text.strip()
        return enhanced_prompt
    except Exception as e:
        # Handle errors gracefully
        return f"Error: {str(e)}"

# Function to download the image
def download_image(image_url, save_path='image.jpg', retries=3, delay=2):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(image_url)
            response.raise_for_status()  # Raise an exception for bad status codes
            with open(save_path, 'wb') as file:
                file.write(response.content)
            return save_path
        except requests.exceptions.RequestException:
            attempt += 1
            if attempt >= retries:
                return "Error: Failed to download image after multiple attempts"
            time.sleep(delay)  # Wait before retrying

# Main function for Streamlit app
def main():
    st.title("Imager ✨")
    st.markdown("Customize and generate a unique image with your preferred details!")

    # Enable/Disable AI Prompt Toggle
    enable_ai = st.checkbox("Enable AI Prompt", value=True)

    # Get user input for the prompt and other image settings
    prompt = st.text_input("Enter the image description (prompt):")
   
    # Use sliders for width, height, and seed values
    col1, col2 = st.columns(2)
    with col1:
        width = st.slider("Width", 256, 1024, 768)
    with col2:
        height = st.slider("Height", 256, 1024, 768)

    seed = st.slider("Seed", 1, 1000, 42)

    # Model selection
    model = st.selectbox("Select a model", [
        "Flux", "Flux-Pro", "Flux-Realism", "Flux-Anime", "Flux-3D", "Flux-CablyAl", "Turbo"
    ])

    # Generate enhanced prompt if AI is enabled
    if enable_ai and prompt:
        enhanced_prompt = generate_enhanced_prompt(prompt)
        st.markdown("### Enhanced Image Description:")
        st.write(enhanced_prompt)
    elif not enable_ai:
        st.markdown("### AI Prompt is Disabled")
        enhanced_prompt = prompt if prompt else "A beautiful 3D scene of a futuristic city"  # Use default if no prompt

    # Image generation button with a loading spinner
    if st.button("Generate Image"):
        with st.spinner("Generating your image..."):
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width={width}&height={height}&seed={seed}&model={model}"
            image_path = download_image(image_url)

            if "Error" in image_path:
                st.error(f"Failed to generate image: {image_path}")
            else:
                watermark_removed_path = remove_watermark(image_path)
                if isinstance(watermark_removed_path, str) and "Error" in watermark_removed_path:
                    st.error(watermark_removed_path)
                else:
                    watermark_removed_image = remove_watermark(image_path)
                    if "Error" in watermark_removed_image:
                        st.error(f"Error during image generation: {watermark_removed_image}")
                    else:
                         upscaled_image = upscale_image(watermark_removed_image, prompta, seed, upscale_factor)
                        if "Error" in upscaled_image:
                            st.error(f"Error during image generation: {upscaled_image}")
                        else:
                            st.image(upscaled_image, use_container_width=True)
                            st.success("Image generated successfully!")
                        

# Run the app
if __name__ == "__main__":
    main()
