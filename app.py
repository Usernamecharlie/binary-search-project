import gradio as gr

def render_array_html(arr, low, high, mid, found_index):
    """
    Helper function to generate HTML for the array visualization.
    It creates a row of boxes with specific colors based on the search state.
    """
    if not arr:
        return "<div style='text-align:center'>Enter numbers to start</div>"
    
    html = "<div style='display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;'>"
    
    for i, val in enumerate(arr):
        # Default style for a box
        color = "#f0f0f0"  # Light grey (default background)
        border = "2px solid #ccc"
        opacity = "1.0"
        font_weight = "normal"
        text_color = "black"
        
        # LOGIC: Determine color based on Binary Search State
        
        # 1. If we found the target, highlight it GREEN
        if i == found_index:
            color = "#4CAF50" # Green
            text_color = "white"
            font_weight = "bold"
            border = "2px solid #2E7D32"
            
        # 2. If this element is the current 'Midpoint' being checked, highlight YELLOW
        elif i == mid:
            color = "#FFEB3B" # Yellow
            border = "2px solid #FBC02D"
            font_weight = "bold"
            
        # 3. If the element is outside the current search range (low to high), Fade it out (GREY)
        elif i < low or i > high:
            color = "#e0e0e0" # Darker grey
            opacity = "0.4"   # Faded look
            border = "1px dashed #999"
            
        # 4. Active search range elements (candidate pool) remain White/Light
        else:
            color = "#ffffff" # White
            border = "2px solid #2196F3" # Blue border for active zone

        # Create the HTML box
        box_html = f"""
        <div style='
            background-color: {color}; 
            border: {border}; 
            opacity: {opacity};
            color: {text_color};
            font-weight: {font_weight};
            padding: 15px; 
            min-width: 40px; 
            text-align: center; 
            border-radius: 8px;
            font-family: sans-serif;
            font-size: 18px;
        '>
            <div style='font-size: 12px; color: #555; margin-bottom: 5px;'>idx: {i}</div>
            {val}
        </div>
        """
        html += box_html
        
    html += "</div>"
    return html

def initialize_search(num_str, target_str):
    """
    Step 1 & 2 (Decomposition): Parse input, sort, and initialize variables.
    """
    try:
        # Input Validation
        if not num_str.strip():
            # FIX B: If input is empty, disable the 'Next' button (interactive=False)
            return (None, "⚠️ Please enter a list of numbers.", "", gr.update(interactive=False))
        
        # Convert string "1, 5, 3" -> list [1, 3, 5]
        arr = sorted([int(x.strip()) for x in num_str.split(',') if x.strip()])
        target = int(target_str)
        
        # Initial State Definition
        state = {
            "arr": arr,
            "target": target,
            "low": 0,
            "high": len(arr) - 1,
            "mid": None,
            "found_index": None,
            "finished": False,
            "step_count": 0,
            "log": "✅ <b>Initialization:</b> List sorted and loaded. Ready to search."
        }
        
        # Render initial visual
        visual_html = render_array_html(arr, 0, len(arr)-1, None, None)
        
        return (state, state["log"], visual_html, gr.update(interactive=True))
        
    except (ValueError, TypeError): 
        # FIX D: Catch TypeError as well (in case target is None)
        return (None, "❌ Error: Please enter valid integers only.", "", gr.update(interactive=False))

def next_step(state):
    """
    Step 3 (Pattern Recognition): The 'Loop' logic that runs one step at a time.
    """
    # FIX A: Handle None state explicitly before checking keys to prevent crash
    if state is None:
        return None, "Please click 'Start Search' first.", ""

    if state["finished"]:
        # Show the existing log + completion message
        return state, state["log"] + "<br>🏁 <b>Search Complete.</b> Press Reset to start over.", render_array_html(state["arr"], state["low"], state["high"], state["mid"], state["found_index"])

    arr = state["arr"]
    target = state["target"]
    low = state["low"]
    high = state["high"]
    
    state["step_count"] += 1
    step_num = state["step_count"]
    
    # 1. Check if search space is exhausted
    if low > high:
        state["finished"] = True
        state["mid"] = None
        log_msg = f"Step {step_num}: Low ({low}) > High ({high}).<br>❌ <b>Target {target} not found</b> in the list."
        
        # FIX C: Update the state log so the message persists
        state["log"] = log_msg 
        
        return state, log_msg, render_array_html(arr, low, high, None, None)

    # 2. Calculate Midpoint
    mid = (low + high) // 2
    state["mid"] = mid
    mid_val = arr[mid]
    
    # 3. Comparison Logic (The "Teacher" explanation)
    log_msg = f"<b>Step {step_num}:</b> Searching range [{low} ... {high}].<br>"
    log_msg += f"👉 Checking Midpoint at index <b>{mid}</b> (Value: <b>{mid_val}</b>).<br>"
    
    if mid_val == target:
        state["found_index"] = mid
        state["finished"] = True
        log_msg += f"🎉 <b>MATCH!</b> Found target {target} at index {mid}."
    elif mid_val < target:
        log_msg += f"📉 {mid_val} < {target}. The target is larger.<br>"
        log_msg += "🗑️ <b>Discarding left half.</b> Updating Low to Mid + 1."
        state["low"] = mid + 1
    else:
        log_msg += f"📈 {mid_val} > {target}. The target is smaller.<br>"
        log_msg += "🗑️ <b>Discarding right half.</b> Updating High to Mid - 1."
        state["high"] = mid - 1

    state["log"] = log_msg
    
    # Render with new state
    visual_html = render_array_html(arr, state["low"], state["high"], state["mid"], state["found_index"])
    
    return state, log_msg, visual_html

def reset_app():
    return None, "Application Reset. Enter new numbers.", "", gr.update(interactive=False)

# --- GRADIO UI LAYOUT ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔍 Interactive Binary Search Visualizer")
    gr.Markdown("An educational tool to demonstrate the **Divide & Conquer** strategy.")
    
    # Session State to hold memory between clicks
    algo_state = gr.State(value=None)
    
    with gr.Row():
        with gr.Column(scale=1):
            input_list = gr.Textbox(label="List of Numbers (comma separated)", placeholder="e.g. 1, 3, 5, 7, 9, 11, 13", value="1, 3, 5, 7, 9, 11, 13, 15, 17")
            target_num = gr.Number(label="Target Number", value=11, precision=0)
            
            with gr.Row():
                btn_start = gr.Button("🚀 Start Search", variant="primary")
                btn_reset = gr.Button("🔄 Reset", variant="secondary")
                
        with gr.Column(scale=2):
            # The HTML Container for the visualization
            visual_box = gr.HTML(label="Visual Representation")
            
            # The Text Log for explanations
            log_box = gr.Markdown("Enter numbers and click 'Start Search' to begin.")
            
            btn_next = gr.Button("⏭️ Next Step", variant="primary", interactive=False)

    # --- EVENTS ---
    
    # 1. Start Button: Validates and Initializes
    btn_start.click(
        fn=initialize_search,
        inputs=[input_list, target_num],
        outputs=[algo_state, log_box, visual_box, btn_next]
    )
    
    # 2. Next Step Button: Advances the algorithm
    btn_next.click(
        fn=next_step,
        inputs=[algo_state],
        outputs=[algo_state, log_box, visual_box]
    )
    
    # 3. Reset Button
    btn_reset.click(
        fn=reset_app,
        inputs=[],
        outputs=[algo_state, log_box, visual_box, btn_next]
    )

if __name__ == "__main__":
    demo.launch()
