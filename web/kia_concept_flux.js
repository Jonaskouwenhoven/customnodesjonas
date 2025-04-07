import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "KiaConceptFlux",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Target the correct node name that matches your workflow
        if (nodeData.name === "KiaConceptClipTextEncodeFlux") {
            // Store the original onNodeCreated function
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                const self = this;
                
                // Log the widget structure to see what we're working with
                console.log("KiaConceptClipTextEncodeFlux widgets:", self.widgets);
                
                // We need to update the UI when inputs are changed
                // Store the original onExecuted function to call it later
                const origOnExecuted = this.onExecuted;
                
                this.onExecuted = function(message) {
                    // Call original onExecuted if it exists
                    if (origOnExecuted) {
                        origOnExecuted.call(this, message);
                    }
                    
                    console.log("Node executed with message:", message);
                    
                    // Update widgets with the new prompts when message contains them
                    if (message && message.clip_prompt) {
                        // Find the clip_l widget (index 3 based on the widget order)
                        const clipWidget = self.widgets[3];
                        if (clipWidget) {
                            clipWidget.value = message.clip_prompt;
                            console.log("Updated clip_l widget with:", message.clip_prompt);
                        }
                    }
                    
                    if (message && message.t5xxl_prompt) {
                        // Find the t5xxl widget (index 4 based on the widget order)
                        const t5xxlWidget = self.widgets[4];
                        if (t5xxlWidget) {
                            t5xxlWidget.value = message.t5xxl_prompt;
                            console.log("Updated t5xxl widget with:", message.t5xxl_prompt);
                        }
                    }
                    
                    // Mark the canvas as dirty to trigger a redraw
                    if (message && (message.clip_prompt || message.t5xxl_prompt)) {
                        app.graph.setDirtyCanvas(true, false);
                    }
                };
                
                // Add theme and strength change listeners
                // Theme is likely widget index 0, strength is likely widget index 1
                if (self.widgets && self.widgets.length > 1) {
                    // Theme listener (index 0)
                    const themeWidget = self.widgets[0];
                    if (themeWidget) {
                        const origThemeCallback = themeWidget.callback;
                        themeWidget.callback = function(v) {
                            console.log("Theme changed to:", v);
                            const result = origThemeCallback ? origThemeCallback.call(this, v) : undefined;
                            // Trigger node execution to update prompts
                            setTimeout(() => {
                                app.graph.setDirtyCanvas(true, true);
                                app.graph.runStep(); // Run the graph to update
                            }, 10);
                            return result;
                        };
                    }
                    
                    // Strength listener (index 1)
                    const strengthWidget = self.widgets[1];
                    if (strengthWidget) {
                        const origStrengthCallback = strengthWidget.callback;
                        strengthWidget.callback = function(v) {
                            console.log("Strength changed to:", v);
                            const result = origStrengthCallback ? origStrengthCallback.call(this, v) : undefined;
                            // Trigger node execution to update prompts
                            setTimeout(() => {
                                app.graph.setDirtyCanvas(true, true);
                                app.graph.runStep(); // Run the graph to update
                            }, 10);
                            return result;
                        };
                    }
                }
                
                return result;
            };
            
            // Override the original getExtraMenuOptions
            const getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function(_, options) {
                if (getExtraMenuOptions) {
                    getExtraMenuOptions.apply(this, arguments);
                }
                
                // Add a refresh option in the context menu
                options.push({
                    content: "Refresh Prompts",
                    callback: () => {
                        // Trigger a re-execution of the node
                        this.setDirtyCanvas(true, true);
                        app.graph.runStep(); // Run the graph to update
                    }
                });
            };
        }
    }
});