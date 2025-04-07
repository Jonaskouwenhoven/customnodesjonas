import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "KiaConceptFlux",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // Update to target both node types
        if (nodeData.name === "KiaFluxConceptNode" || nodeData.name === "CLIPTextEncodeFlux") {
            // Add a widget dynamically for clip_l and t5xxl
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                
                const self = this;
                
                // Add widgets if they don't exist already
                // Check if this node needs widgets (KiaFluxConceptNode already has them defined in Python)
                if (nodeData.name === "CLIPTextEncodeFlux") {
                    // Add clip_l widget if it doesn't exist
                    if (!this.widgets.find(w => w.name === "clip_l")) {
                        this.addWidget("text", "clip_l", "", function(v) {
                            // Handle value changes
                        }, { multiline: true });
                    }
                    
                    // Add t5xxl widget if it doesn't exist
                    if (!this.widgets.find(w => w.name === "t5xxl")) {
                        this.addWidget("text", "t5xxl", "", function(v) {
                            // Handle value changes
                        }, { multiline: true });
                    }
                }
                
                // We need to update the UI when inputs are changed
                // Store the original onExecuted function to call it later
                const origOnExecuted = this.onExecuted;
                
                this.onExecuted = function(message) {
                    // Call original onExecuted if it exists
                    if (origOnExecuted) {
                        origOnExecuted.call(this, message);
                    }
                    
                    // If this is a KiaFluxConceptNode, handle theme/preset changes
                    if (nodeData.name === "KiaFluxConceptNode") {
                        // Find the clip_l and t5xxl widgets by name
                        const clipWidget = self.widgets.find(w => w.name === "clip_l");
                        const t5xxlWidget = self.widgets.find(w => w.name === "t5xxl");
                        
                        // Update widgets with the new prompts when message contains them
                        if (message && message.clip_prompt && clipWidget) {
                            clipWidget.value = message.clip_prompt;
                        }
                        if (message && message.t5xxl_prompt && t5xxlWidget) {
                            t5xxlWidget.value = message.t5xxl_prompt;
                        }
                        
                        // Mark the canvas as dirty to trigger a redraw
                        if (message && (message.clip_prompt || message.t5xxl_prompt)) {
                            this.setDirtyCanvas(true, false);
                        }
                    }
                    // For CLIPTextEncodeFlux, handle the message directly
                    else if (nodeData.name === "CLIPTextEncodeFlux") {
                        if (message && message.clip_prompt) {
                            self.widgets[3].value = message.clip_prompt;
                        }
                        if (message && message.t5xxl_prompt) {
                            self.widgets[4].value = message.t5xxl_prompt;
                        }
                    }
                };
                
                // For KiaFluxConceptNode, add listeners for theme/preset selection changes
                if (nodeData.name === "KiaFluxConceptNode") {
                    // Get the theme and preset widgets
                    const themeWidget = self.widgets.find(w => w.name === "theme");
                    const presetWidget = self.widgets.find(w => w.name === "preset");
                    
                    // If found, add listeners to trigger a node execution when they change
                    if (themeWidget) {
                        const origThemeCallback = themeWidget.callback;
                        themeWidget.callback = function(v) {
                            const result = origThemeCallback ? origThemeCallback.call(this, v) : undefined;
                            // Trigger node execution to update prompts
                            setTimeout(() => {
                                self.setDirtyCanvas(true, true);
                                app.graph.runStep(); // Run the graph to update
                            }, 10);
                            return result;
                        };
                    }
                    
                    if (presetWidget) {
                        const origPresetCallback = presetWidget.callback;
                        presetWidget.callback = function(v) {
                            const result = origPresetCallback ? origPresetCallback.call(this, v) : undefined;
                            // Trigger node execution to update prompts
                            setTimeout(() => {
                                self.setDirtyCanvas(true, true);
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