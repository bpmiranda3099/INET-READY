<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { saveMedicalData } from '$lib/services/medical-api.js';
    
    export let initialData: any = null;
    export let isEditing: boolean = false;
    
    const dispatch = createEventDispatcher();
    
    let loading = false;
    let error = null;
    let success = false;
    
    // Constants for unit conversion
    const ML_PER_CUP = 237; // 1 cup = 237 ml (approximately)
    
    // Medical conditions and medications organized into categories
    const medicalConditionCategories = [
        { 
            name: 'Cardiovascular', 
            icon: '❤️',
            conditions: [
                { id: 'cardiovascular_disease', label: 'Cardiovascular Disease', icon: '🫀' },
                { id: 'high_blood_pressure', label: 'High Blood Pressure', icon: '❤️‍🔥' }
            ]
        },
        { 
            name: 'Metabolic', 
            icon: '⚡',
            conditions: [
                { id: 'diabetes', label: 'Diabetes', icon: '💉' },
                { id: 'thyroid_disorder', label: 'Thyroid Disorder', icon: '🦋' }
            ]
        },
        { 
            name: 'Respiratory', 
            icon: '🫁',
            conditions: [
                { id: 'respiratory_issues', label: 'Respiratory Issues', icon: '🤧' },
                { id: 'asthma', label: 'Asthma', icon: '😤' }
            ]
        },
        { 
            name: 'Other Conditions',
            icon: '⚠️', 
            conditions: [
                { id: 'heat_sensitivity', label: 'Heat Sensitivity', icon: '☀️' },
                { id: 'kidney_disease', label: 'Kidney Disease', icon: '🩸' },
                { id: 'neurological_disorders', label: 'Neurological Disorders', icon: '🧠' }
            ]
        }
    ];
    
    const medicationCategories = [
        {
            name: 'Common Medications',
            icon: '💊',
            medications: [
                { id: 'diuretics', label: 'Diuretics', icon: '💧' },
                { id: 'blood_pressure_medications', label: 'Blood Pressure Medications', icon: '❤️' },
                { id: 'antihistamines', label: 'Antihistamines', icon: '🤧' },
                { id: 'antidepressants', label: 'Antidepressants', icon: '🧠' },
                { id: 'antipsychotics', label: 'Antipsychotics', icon: '💫' }
            ]
        }
    ];
    
    // Drink types for fluid intake
    const drinkTypes = [
        { id: 'water', label: 'Water', icon: '💧' },
        { id: 'electrolyte_drinks', label: 'Electrolyte Drinks', icon: '🧪' },
        { id: 'coconut_water', label: 'Coconut Water', icon: '🥥' },
        { id: 'fruit_juice', label: 'Fruit Juice', icon: '🍊' },
        { id: 'iced_tea', label: 'Iced Tea', icon: '🍵' },
        { id: 'soda', label: 'Soda', icon: '🥤' },
        { id: 'milk_tea', label: 'Milk Tea', icon: '🧋' },
        { id: 'coffee', label: 'Coffee', icon: '☕' },
        { id: 'herbal_tea', label: 'Herbal Tea', icon: '🌿' }
    ];
    
    // Activity level options
    const activityLevels = [
        { id: 'sedentary', label: 'Sedentary (little or no exercise)' },
        { id: 'light', label: 'Light (exercise 1-3 days/week)' },
        { id: 'moderate', label: 'Moderate (exercise 3-5 days/week)' },
        { id: 'vigorous', label: 'Vigorous (exercise 6-7 days/week)' },
        { id: 'extreme', label: 'Extreme (professional athlete level)' }
    ];
    
    // Form data structure with improved organization
    let medicalData = initialData || {
        demographics: {
            age: '',
            gender: 'prefer-not-to-say'
        },
        biometrics: {
            height: '',
            weight: ''
        },
        medical_conditions: {
            cardiovascular_disease: false,
            diabetes: false,
            respiratory_issues: false,
            heat_sensitivity: false,
            kidney_disease: false,
            neurological_disorders: false,
            high_blood_pressure: false,
            thyroid_disorder: false,
            asthma: false,
            other: {
                has_other: false,
                description: ''
            }
        },
        medications: {
            diuretics: false,
            blood_pressure_medications: false,
            antihistamines: false,
            antidepressants: false,
            antipsychotics: false,
            other: {
                has_other: false,
                description: ''
            }
        },
        fluid_intake: {
            // Convert from ml to cups for sliders (will convert back when saving)
            water_cups: 0,
            electrolyte_drinks_cups: 0,
            coconut_water_cups: 0,
            fruit_juice_cups: 0,
            iced_tea_cups: 0,
            soda_cups: 0,
            milk_tea_cups: 0,
            coffee_cups: 0,
            herbal_tea_cups: 0,
            other: {
                has_other: false,
                name: '',
                cups: 0
            }
        },
        heat_conditions: {
            mild_dehydration: false,
            heat_rash: false,
            heat_stroke: false,
            muscle_fatigue: false,
            heat_syncope: false,
            heat_edema: false,
            heat_exhaustion: false
        },
        activity: {
            previous_heat_issues: false,
            heat_issues_details: '',
            outdoor_activity: false,
            activity_level: 'sedentary',
            activity_duration: {
                value: 30,
                unit: 'minutes'
            }
        }
    };
    
    // Initialize or check for undefined properties in initialData
    function initializeMedicalData() {
        // If initialData was provided, make sure all the necessary nested objects exist
        if (initialData) {            
            // Initialize fluid_intake if it doesn't exist
            if (!medicalData.fluid_intake) {
                medicalData.fluid_intake = {
                    water_cups: 0,
                    electrolyte_drinks_cups: 0,
                    coconut_water_cups: 0,
                    fruit_juice_cups: 0,
                    iced_tea_cups: 0,
                    soda_cups: 0,
                    milk_tea_cups: 0,
                    coffee_cups: 0,
                    herbal_tea_cups: 0,
                    other: { has_other: false, name: '', cups: 0 }
                };
            }
            
            // Initialize the other object within fluid_intake if it doesn't exist
            if (!medicalData.fluid_intake.other) {
                medicalData.fluid_intake.other = { has_other: false, name: '', cups: 0 };
            }
            
            // Initialize medical_conditions if it doesn't exist
            if (!medicalData.medical_conditions) {
                medicalData.medical_conditions = {
                    cardiovascular_disease: false,
                    diabetes: false,
                    respiratory_issues: false,
                    heat_sensitivity: false,
                    kidney_disease: false,
                    neurological_disorders: false,
                    high_blood_pressure: false,
                    thyroid_disorder: false,
                    asthma: false,
                    other: { has_other: false, description: '' }
                };
            }
            
            // Initialize the other object within medical_conditions if it doesn't exist
            if (!medicalData.medical_conditions.other) {
                medicalData.medical_conditions.other = { has_other: false, description: '' };
            }
            
            // Initialize medications if it doesn't exist
            if (!medicalData.medications) {
                medicalData.medications = {
                    diuretics: false,
                    blood_pressure_medications: false,
                    antihistamines: false,
                    antidepressants: false,
                    antipsychotics: false,
                    other: { has_other: false, description: '' }
                };
            }
            
            // Initialize the other object within medications if it doesn't exist
            if (!medicalData.medications.other) {
                medicalData.medications.other = { has_other: false, description: '' };
            }
            
            // Initialize standard drink cups if they don't exist
            for (const drink of drinkTypes) {
                const cupField = `${drink.id}_cups`;
                if (medicalData.fluid_intake[cupField] === undefined) {
                    medicalData.fluid_intake[cupField] = 0;
                }
            }
        }
    }
    
    // Initialize data to ensure all required structures exist
    if (initialData) {
        // Make sure all required objects exist in the fluid intake section
        if (!medicalData.fluid_intake) {
            medicalData.fluid_intake = {
                water_cups: 0,
                electrolyte_drinks_cups: 0,
                coconut_water_cups: 0,
                fruit_juice_cups: 0,
                iced_tea_cups: 0,
                soda_cups: 0,
                milk_tea_cups: 0,
                coffee_cups: 0,
                herbal_tea_cups: 0,
                other: { has_other: false, name: '', cups: 0 }
            };
        } else if (!medicalData.fluid_intake.other) {
            medicalData.fluid_intake.other = { has_other: false, name: '', cups: 0 };
        }
        
        // Ensure all drink cup properties exist
        for (const drink of drinkTypes) {
            const cupField = `${drink.id}_cups`;
            if (medicalData.fluid_intake[cupField] === undefined) {
                medicalData.fluid_intake[cupField] = 0;
            }
        }
        
        // Make sure medical conditions structure exists
        if (!medicalData.medical_conditions) {
            medicalData.medical_conditions = {
                cardiovascular_disease: false,
                diabetes: false,
                respiratory_issues: false,
                heat_sensitivity: false,
                kidney_disease: false,
                neurological_disorders: false,
                high_blood_pressure: false,
                thyroid_disorder: false,
                asthma: false,
                other: { has_other: false, description: '' }
            };
        } else if (!medicalData.medical_conditions.other) {
            medicalData.medical_conditions.other = { has_other: false, description: '' };
        }
        
        // Make sure medications structure exists
        if (!medicalData.medications) {
            medicalData.medications = {
                diuretics: false,
                blood_pressure_medications: false,
                antihistamines: false,
                antidepressants: false,
                antipsychotics: false,
                other: { has_other: false, description: '' }
            };
        } else if (!medicalData.medications.other) {
            medicalData.medications.other = { has_other: false, description: '' };
        }
    }
    
    // Fix activity_duration if it's a string (from database) instead of an object (as expected by the form)
    if (initialData && typeof initialData === 'object' && initialData.activity && 
        typeof initialData.activity.activity_duration === 'string') {
        // Convert string format from database to the object format expected by the form
        let durationValue = 30; // Default to 30 minutes
        
        switch (initialData.activity.activity_duration) {
            case 'less_than_30_mins':
                durationValue = 20;
                break;
            case '30_to_60_mins':
                durationValue = 45;
                break;
            case '1_to_2_hours':
                durationValue = 90;
                break;
            case 'more_than_2_hours':
                durationValue = 150;
                break;
        }
        
        // Replace the string with an object having value and unit properties
        medicalData.activity.activity_duration = {
            value: durationValue,
            unit: 'minutes'
        };
    }
    
    // Function to ensure activity_duration is properly converted from string to object format
    function ensureValidActivityDuration() {
        if (medicalData?.activity) {
            if (typeof medicalData.activity.activity_duration === 'string') {
                // Convert string format to object format
                let durationValue = 30; // Default
                
                switch (medicalData.activity.activity_duration) {
                    case 'less_than_30_mins':
                        durationValue = 20;
                        break;
                    case '30_to_60_mins':
                        durationValue = 45;
                        break;
                    case '1_to_2_hours':
                        durationValue = 90;
                        break;
                    case 'more_than_2_hours':
                        durationValue = 150;
                        break;
                }
                
                // Replace the string with an object
                medicalData.activity.activity_duration = {
                    value: durationValue,
                    unit: 'minutes'
                };
            }
        }
    }
    
    // Call after initialization
    ensureValidActivityDuration();
    
    // Call initialization function immediately after medicalData is created
    initializeMedicalData();
    
    // Form validation
    function validateForm() {
        // Required fields validation
        if (!medicalData.demographics.age) {
            error = "Please enter your age";
            return false;
        }
        
        if (!medicalData.biometrics.height) {
            error = "Please enter your height";
            return false;
        }
        
        if (!medicalData.biometrics.weight) {
            error = "Please enter your weight";
            return false;
        }
        
        return true;
    }
    
    // Handle form submission
    async function handleSubmit() {
        error = null;
        success = false;
        
        if (!validateForm()) return;
        
        loading = true;
        
        try {
            // Convert cups back to milliliters for storage
            const processedFluidIntake: Record<string, any> = {};
            
            // Process standard drinks
            for (const drinkType of drinkTypes) {
                const cupsField = drinkType.id + '_cups';
                const mlField = drinkType.id + '_amount';
                processedFluidIntake[mlField] = Math.round(medicalData.fluid_intake[cupsField] * ML_PER_CUP);
            }
            
            // Process other drinks
            if (medicalData.fluid_intake.other.has_other) {
                processedFluidIntake.other_fluid = medicalData.fluid_intake.other.name;
                processedFluidIntake.other_fluid_amount = Math.round(medicalData.fluid_intake.other.cups * ML_PER_CUP);
            }
            
            // Process activity duration
            let activityDuration;
            const durationMins = medicalData.activity.activity_duration.value;
            
            if (durationMins < 30) {
                activityDuration = 'less_than_30_mins';
            } else if (durationMins >= 30 && durationMins < 60) {
                activityDuration = '30_to_60_mins';
            } else if (durationMins >= 60 && durationMins <= 120) {
                activityDuration = '1_to_2_hours';
            } else {
                activityDuration = 'more_than_2_hours';
            }
            
            // Prepare final data
            const processedData = {
                demographics: {
                    ...medicalData.demographics,
                    age: Number(medicalData.demographics.age)
                },
                biometrics: {
                    ...medicalData.biometrics,
                    height: Number(medicalData.biometrics.height),
                    weight: Number(medicalData.biometrics.weight)
                },
                medical_conditions: medicalData.medical_conditions,
                medications: medicalData.medications,
                fluid_intake: processedFluidIntake,
                heat_conditions: medicalData.heat_conditions,
                activity: {
                    ...medicalData.activity,
                    activity_duration: activityDuration
                }
            };
            
            // Use new API client (no userId needed)
            await saveMedicalData(processedData);
            success = true;
            dispatch('completed', { success: true });
        } catch (err) {
            console.error("Error saving medical data:", err);
            error = err?.message || "An unexpected error occurred. Please try again.";
        } finally {
            loading = false;
        }
    }
    
    function handleCancel() {
        dispatch('cancel');
    }
    
    // Format cup value for display
    function formatCups(cups) {
        if (cups === 0) return '0 cups';
        if (cups === 1) return '1 cup';
        return `${cups} cups`;
    }
    
    // Format minutes value for display
    function formatDuration(minutes) {
        if (minutes < 60) {
            return `${minutes} min`;
        } else {
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
        }
    }
</script>

<div class="medical-form-container"></div>
    <div class="form-header">
        <h2>{isEditing ? 'Update Medical Information' : 'Complete Your Medical Profile'}</h2>
        {#if !isEditing}
            <p class="form-intro">
                To help us provide personalized insights about your hydration needs, please
                fill out the following health information. Your data is kept private and secure.
            </p>
        {/if}
    </div>
    
    {#if error}
        <div class="alert error-alert">
            <div class="alert-icon">⚠️</div>
            <div class="alert-content">{error}</div>
        </div>
    {/if}
    
    {#if success}
        <div class="alert success-alert">
            <div class="alert-icon">✅</div>
            <div class="alert-content">Your medical data has been successfully saved!</div>
        </div>
    {/if}
    
    <form on:submit|preventDefault={handleSubmit}>
        <!-- Demographics & Biometrics Section -->
        <div class="section-container">
            <div class="section-header">
                <h3>Demographics & Biometrics</h3>
            </div>
            <div class="section-body">
                <div class="form-grid">
                    <div class="form-field">
                        <label for="age">
                            <div class="label-icon">📅</div>
                            <span>Age <span class="required">*</span></span>
                        </label>
                        <input 
                            type="number" 
                            id="age" 
                            bind:value={medicalData.demographics.age} 
                            min="1" 
                            max="120"
                            required
                            class="modern-input"
                        />
                    </div>
                    
                    <div class="form-field">
                        <label for="gender">
                            <div class="label-icon">👤</div>
                            <span>Gender</span>
                        </label>
                        <select id="gender" bind:value={medicalData.demographics.gender} class="modern-select">
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="non-binary">Non-binary</option>
                            <option value="prefer-not-to-say">Prefer not to say</option>
                        </select>
                    </div>
                    
                    <div class="form-field">
                        <label for="height">
                            <div class="label-icon">📏</div>
                            <span>Height (cm) <span class="required">*</span></span>
                        </label>
                        <input 
                            type="number" 
                            id="height" 
                            bind:value={medicalData.biometrics.height} 
                            min="50" 
                            max="250"
                            required
                            class="modern-input"
                        />
                    </div>
                    
                    <div class="form-field">
                        <label for="weight">
                            <div class="label-icon">⚖️</div>
                            <span>Weight (kg) <span class="required">*</span></span>
                        </label>
                        <input 
                            type="number" 
                            id="weight" 
                            bind:value={medicalData.biometrics.weight} 
                            min="1" 
                            max="500"
                            required
                            class="modern-input"
                        />
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Medical Conditions Section -->
        <div class="section-container">
            <div class="section-header">
                <h3>Medical Conditions</h3>
            </div>
            <div class="section-body">
                <div class="section-info">Select any conditions that apply to you</div>
                
                {#each medicalConditionCategories as category}
                    <div class="condition-category">
                        <div class="category-header">
                            <span class="category-title"><span class="category-icon">{category.icon}</span>{category.name}</span>
                        </div>
                        <div class="condition-cards">
                            {#each category.conditions as condition}
                                <label class="condition-card" class:selected={medicalData.medical_conditions[condition.id]}>
                                    <input 
                                        type="checkbox" 
                                        bind:checked={medicalData.medical_conditions[condition.id]}
                                        class="hidden-checkbox"
                                    />
                                    <div class="condition-icon">{condition.icon}</div>
                                    <span class="condition-label">{condition.label}</span>
                                </label>
                            {/each}
                        </div>
                    </div>
                {/each}
                
                <!-- Other conditions -->
                <div class="other-condition">
                    <label class="other-checkbox">
                        <input 
                            type="checkbox" 
                            bind:checked={medicalData.medical_conditions.other.has_other}
                            class="hidden-checkbox"
                        />
                        <div class="checkbox-visual">
                            <div class="checkbox-indicator"></div>
                        </div>
                        <span>Other condition(s)</span>
                    </label>
                    
                    {#if medicalData.medical_conditions.other.has_other}
                        <div class="other-input-container">
                            <input 
                                type="text" 
                                placeholder="Please describe" 
                                bind:value={medicalData.medical_conditions.other.description}
                                class="modern-input" 
                            />
                        </div>
                    {/if}
                </div>
            </div>
        </div>
        
        <!-- Medications Section -->
        <div class="section-container">
            <div class="section-header">
                <h3>Medications</h3>
            </div>
            <div class="section-body">
                <div class="section-info">Select any medications that you are currently taking</div>
                
                {#each medicationCategories as category}
                    <div class="medication-grid">
                        {#each category.medications as medication}
                            <label class="medication-card" class:selected={medicalData.medications[medication.id]}>
                                <input 
                                    type="checkbox" 
                                    bind:checked={medicalData.medications[medication.id]}
                                    class="hidden-checkbox"
                                />
                                <div class="medication-content">
                                    <div class="medication-icon">{medication.icon}</div>
                                    <span class="medication-name">{medication.label}</span>
                                </div>
                            </label>
                        {/each}
                    </div>
                {/each}
                
                <!-- Other medications -->
                <div class="other-medication">
                    <label class="other-checkbox">
                        <input 
                            type="checkbox" 
                            bind:checked={medicalData.medications.other.has_other}
                            class="hidden-checkbox"
                        />
                        <div class="checkbox-visual">
                            <div class="checkbox-indicator"></div>
                        </div>
                        <span>Other medication(s)</span>
                    </label>
                    
                    {#if medicalData.medications.other.has_other}
                        <div class="other-input-container">
                            <input 
                                type="text" 
                                placeholder="Please describe" 
                                bind:value={medicalData.medications.other.description}
                                class="modern-input" 
                            />
                        </div>
                    {/if}
                </div>
            </div>
        </div>
        
        <!-- Fluid Intake Section -->
        <div class="section-container">
            <div class="section-header">
                <h3>Average Daily Fluid Intake</h3>
            </div>
            <div class="section-body">
                <div class="section-info">Adjust the sliders to indicate how many cups you drink of each fluid type</div>
                
                <div class="fluid-sliders">
                    {#each drinkTypes as drink}
                        {@const fieldName = drink.id + '_cups'}
                        <div class="fluid-slider-item">
                            <div class="slider-header">
                                <div class="drink-info">
                                    <div class="drink-icon">{drink.icon}</div>
                                    <label for={fieldName} class="drink-label">{drink.label}</label>
                                </div>
                                <span class="slider-value">{formatCups(medicalData.fluid_intake[fieldName])}</span>
                            </div>
                            <div class="modern-slider-container">
                                <input 
                                    type="range" 
                                    id={fieldName} 
                                    bind:value={medicalData.fluid_intake[fieldName]} 
                                    min="0" 
                                    max="10"
                                    step="0.5"
                                    class="modern-slider" 
                                />
                                <div class="slider-track">
                                    <div class="slider-progress" style="width: {(medicalData.fluid_intake[fieldName] / 10) * 100}%"></div>
                                </div>
                            </div>
                        </div>
                    {/each}
                    
                    <!-- Other fluid with slider -->
                    <div class="other-fluid">
                        <label class="other-checkbox">
                            <input 
                                type="checkbox" 
                                bind:checked={medicalData.fluid_intake.other.has_other}
                                class="hidden-checkbox"
                            />
                            <div class="checkbox-visual">
                                <div class="checkbox-indicator"></div>
                            </div>
                            <span>Other beverage</span>
                        </label>
                        
                        {#if medicalData.fluid_intake.other.has_other}
                            <div class="other-fluid-details">
                                <input 
                                    type="text" 
                                    placeholder="Name of beverage" 
                                    bind:value={medicalData.fluid_intake.other.name}
                                    class="modern-input" 
                                />
                                <div class="slider-header">
                                    <label for="other_cups" class="drink-label">Amount</label>
                                    <span class="slider-value">{formatCups(medicalData.fluid_intake.other.cups)}</span>
                                </div>
                                <div class="modern-slider-container">
                                    <input 
                                        type="range" 
                                        id="other_cups" 
                                        bind:value={medicalData.fluid_intake.other.cups} 
                                        min="0" 
                                        max="10"
                                        step="0.5"
                                        class="modern-slider" 
                                    />
                                    <div class="slider-track">
                                        <div class="slider-progress" style="width: {(medicalData.fluid_intake.other.cups / 10) * 100}%"></div>
                                    </div>
                                </div>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Heat-Related Conditions Section -->
        <div class="section-container">
            <div class="section-header">
                <h3>Heat-Related Conditions</h3>
            </div>
            <div class="section-body">
                <div class="section-info">Select any conditions you have experienced</div>
                
                <div class="heat-condition-grid">
                    <label class="heat-condition-card" class:selected={medicalData.heat_conditions.mild_dehydration}>
                        <input type="checkbox" bind:checked={medicalData.heat_conditions.mild_dehydration} class="hidden-checkbox">
                        <div class="condition-content">
                            <div class="condition-icon">💧</div>
                            <span class="condition-name">Mild Dehydration</span>
                        </div>
                    </label>
                    
                    <label class="heat-condition-card" class:selected={medicalData.heat_conditions.heat_rash}>
                        <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_rash} class="hidden-checkbox">
                        <div class="condition-content">
                            <div class="condition-icon">🔴</div>
                            <span class="condition-name">Heat Rash</span>
                        </div>
                    </label>
                    
                    <label class="heat-condition-card" class:selected={medicalData.heat_conditions.heat_stroke}>
                        <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_stroke} class="hidden-checkbox">
                        <div class="condition-content">
                            <div class="condition-icon">🔥</div>
                            <span class="condition-name">Heat Stroke</span>
                        </div>
                    </label>
                    
                    <label class="heat-condition-card" class:selected={medicalData.heat_conditions.muscle_fatigue}>
                        <input type="checkbox" bind:checked={medicalData.heat_conditions.muscle_fatigue} class="hidden-checkbox">
                        <div class="condition-content">
                            <div class="condition-icon">😩</div>
                            <span class="condition-name">Muscle Fatigue</span>
                        </div>
                    </label>
                    
                    <label class="heat-condition-card" class:selected={medicalData.heat_conditions.heat_syncope}>
                        <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_syncope} class="hidden-checkbox">
                        <div class="condition-content">
                            <div class="condition-icon">😵</div>
                            <span class="condition-name">Heat Syncope (Fainting)</span>
                        </div>
                    </label>
                    
                    <label class="heat-condition-card" class:selected={medicalData.heat_conditions.heat_edema}>
                        <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_edema} class="hidden-checkbox">
                        <div class="condition-content">
                            <div class="condition-icon">🦶</div>
                            <span class="condition-name">Heat Edema (Swelling)</span>
                        </div>
                    </label>
                    
                    <label class="heat-condition-card" class:selected={medicalData.heat_conditions.heat_exhaustion}>
                        <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_exhaustion} class="hidden-checkbox">
                        <div class="condition-content">
                            <div class="condition-icon">⚡</div>
                            <span class="condition-name">Heat Exhaustion</span>
                        </div>
                    </label>
                </div>
            </div>
        </div>
        
        <!-- Activity & Heat Issues Section -->
        <div class="section-container">
            <div class="section-header">
                <h3>Activity & Heat Issues</h3>
            </div>
            <div class="section-body">
                <!-- Heat issues experience -->
                <div class="heat-issues-question">
                    <label class="modern-checkbox-container">
                        <input 
                            type="checkbox" 
                            bind:checked={medicalData.activity.previous_heat_issues}
                            class="hidden-checkbox"
                        />
                        <div class="modern-checkbox">
                            <div class="checkbox-indicator"></div>
                        </div>
                        <span class="question-text">Have you experienced heat-related health issues in the past?</span>
                    </label>
                </div>
                
                {#if medicalData.activity.previous_heat_issues}
                    <div class="heat-issues-details">
                        <label for="heat_issues_details" class="details-label">Please describe your experience</label>
                        <textarea 
                            id="heat_issues_details" 
                            bind:value={medicalData.activity.heat_issues_details}
                            rows="3"
                            class="modern-textarea"
                        ></textarea>
                    </div>
                {/if}
                
                <!-- Outdoor activity -->
                <div class="outdoor-activity-question">
                    <label class="modern-checkbox-container">
                        <input 
                            type="checkbox" 
                            bind:checked={medicalData.activity.outdoor_activity}
                            class="hidden-checkbox"
                        />
                        <div class="modern-checkbox">
                            <div class="checkbox-indicator"></div>
                        </div>
                        <span class="question-text">Do you regularly engage in outdoor activities?</span>
                    </label>
                </div>
                
                {#if medicalData.activity.outdoor_activity}
                    <div class="activity-details-container">
                        <div class="activity-level-selection">
                            <label for="activity_level" class="activity-label">Activity Level</label>
                            <select 
                                id="activity_level" 
                                bind:value={medicalData.activity.activity_level}
                                class="modern-select"
                            >
                                {#each activityLevels as level}
                                    <option value={level.id}>{level.label}</option>
                                {/each}
                            </select>
                        </div>
                        
                        <div class="duration-selection">
                            <div class="duration-header">
                                <label for="activity_duration" class="duration-label">Average Duration Per Session</label>
                                <span class="duration-value">{formatDuration(medicalData.activity.activity_duration.value)}</span>
                            </div>
                            <div class="modern-slider-container">
                                <input 
                                    type="range" 
                                    id="activity_duration" 
                                    bind:value={medicalData.activity.activity_duration.value} 
                                    min="5" 
                                    max="180"
                                    step="5"
                                    class="modern-slider" 
                                />
                                <div class="slider-track">
                                    <div class="slider-progress" style="width: {(medicalData.activity.activity_duration.value / 180) * 100}%"></div>
                                </div>
                                <div class="slider-labels">
                                    <span>5 min</span>
                                    <span>3 hours</span>
                                </div>
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
        
        <!-- Form Actions -->
        <div class="form-actions">
            {#if isEditing}
                <button type="button" class="cancel-btn" on:click={handleCancel} disabled={loading}>
                    Cancel
                </button>
            {/if}
            
            <button type="submit" class="submit-btn" disabled={loading}>
                {#if loading}
                    <span class="spinner"></span>
                    <span>{isEditing ? 'Updating...' : 'Saving...'}</span>
                {:else}
                    <span>{isEditing ? 'Update Profile' : 'Save Profile'}</span>
                {/if}
            </button>
        </div>
    </form>
    
<style>
    .medical-form-container {
        max-width: 800px;
        margin: 0 auto;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .form-header {
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .form-header h2 {
        margin-bottom: 0.5rem;
        color: #333;
        font-weight: 600;
    }
    
    .form-intro {
        color: #666;
        font-size: 0.95rem;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Alert styles */
    .alert {
        display: flex;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        align-items: center;
    }
    
    .error-alert {
        background-color: #ffeded;
        border-left: 4px solid #e74c3c;
    }
    
    .success-alert {
        background-color: #edfff5;
        border-left: 4px solid #2ecc71;
    }
    
    .alert-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
    }
    
    .alert-content {
        flex: 1;
    }
    
    /* Section container styling - matches the account section styling */
    .section-container {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .section-header {
        background: #dd815e;
        color: white;
        padding: 1rem;
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: center;
        overflow: hidden;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        top: -20px;
        right: -20px;
        width: 120px;
        height: 120px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
    }
    
    .section-header h3 {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        position: relative;
        z-index: 1;
    }
    
    .section-body {
        padding: 1.5rem;
    }
    
    .section-info {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }
    
    /* Form field styles */
    .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 1.5rem;
    }
    
    .form-field {
        display: flex;
        flex-direction: column;
    }
    
    label {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #444;
    }
    
    .label-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }
    
    .required {
        color: #e74c3c;
        margin-left: 2px;
    }
    
    .modern-input, .modern-select, .modern-textarea {
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        font-family: inherit;
        font-size: 1rem;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    
    .modern-input:focus, .modern-select:focus, .modern-textarea:focus {
        border-color: #dd815e;
        box-shadow: 0 0 0 3px rgba(221, 129, 94, 0.2);
        outline: none;
    }
    
    .modern-textarea {
        resize: vertical;
        min-height: 100px;
    }
    
    /* Condition categories */
    .condition-category {
        margin-bottom: 1.5rem;
    }
    
    .category-header {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .category-icon {
        font-size: 1.25rem;
        margin-right: 0.5rem;
    }
    
    .category-title {
        font-weight: 600;
        color: #444;
    }
    
    .condition-cards {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 0.75rem;
    }
    
    .condition-card, .medication-card, .heat-condition-card {
        position: relative;
        display: flex;
        align-items: center;
        padding: 0.75rem;
        background-color: #f9f9f9;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .condition-card:hover, .medication-card:hover, .heat-condition-card:hover {
        background-color: #f0f0f0;
    }
    
    .condition-content, .medication-content {
        display: flex;
        align-items: center;
        width: 100%;
    }
    
    .condition-icon, .medication-icon {
        font-size: 1.2rem;
        margin-right: 0.75rem;
    }
    
    .condition-name, .medication-name {
        flex: 1;
    }
    
    /* Custom checkboxes */
    .hidden-checkbox {
        position: absolute;
        opacity: 0;
        cursor: pointer;
    }
    
    .checkbox-visual {
        width: 22px;
        height: 22px;
        min-width: 22px;
        background-color: white;
        border: 2px solid #ddd;
        border-radius: 6px;
        margin-right: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    
    .checkbox-indicator {
        width: 12px;
        height: 12px;
        background-color: #dd815e;
        border-radius: 3px;
        opacity: 0;
        transition: opacity 0.2s;
    }
    
    .hidden-checkbox:checked + .checkbox-visual {
        border-color: #dd815e;
    }
    
    .hidden-checkbox:checked + .checkbox-visual .checkbox-indicator,
    .hidden-checkbox:checked + .condition-content .checkbox-indicator,
    .hidden-checkbox:checked + .medication-content .checkbox-indicator {
        opacity: 1;
    }
    
    /* Medication grid */
    .medication-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    /* Heat condition grid */
    .heat-condition-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 0.75rem;
    }
    
    /* Modern checkbox container */
    .modern-checkbox-container {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        cursor: pointer;
    }
    
    .modern-checkbox {
        width: 24px;
        height: 24px;
        min-width: 24px;
        background-color: white;
        border: 2px solid #ddd;
        border-radius: 6px;
        margin-right: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    
    .question-text {
        font-weight: 500;
        color: #444;
    }
    
    /* Other field styles */
    .other-condition, .other-medication, .other-fluid {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
    
    .other-checkbox {
        display: flex;
        align-items: center;
        margin-bottom: 0.75rem;
        cursor: pointer;
    }
    
    .other-input-container, .other-fluid-details {
        margin-left: 2.25rem;
        margin-top: 0.75rem;
    }
    
    /* Fluid sliders */
    .fluid-sliders {
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
    }
    
    .fluid-slider-item {
        display: flex;
        flex-direction: column;
    }
    
    .slider-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .drink-info {
        display: flex;
        align-items: center;
    }
    
    .drink-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
    
    .drink-label {
        font-weight: 500;
        color: #444;
    }
    
    .slider-value {
        font-weight: 600;
        color: #dd815e;
    }
    
    /* Modern slider */
    .modern-slider-container {
        position: relative;
        height: 36px;
        display: flex;
        align-items: center;
    }
    
    .modern-slider {
        -webkit-appearance: none;
        width: 100%;
        height: 6px;
        background: transparent;
        outline: none;
        position: absolute;
        z-index: 2;
        border: 0px;
    }
    
    .slider-track {
        position: absolute;
        width: 100%;
        height: 6px;
        background-color: #eee;
        border-radius: 3px;
        z-index: 1;
    }
    
    .slider-progress {
        position: absolute;
        height: 6px;
        background-color: #dd815e;
        border-radius: 3px;
        z-index: 1;
    }
    
    .modern-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 18px;
        height: 18px;
        background: #dd815e;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: transparent;
        transition: background 0.2s;
    }
    
    .modern-slider::-moz-range-thumb {
        width: 18px;
        height: 18px;
        background: #dd815e;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: transparent;
        transition: background 0.2s;
        border: none;
    }
    
    .modern-slider::-webkit-slider-thumb:hover {
        background: #c9704f;
    }
    
    .modern-slider::-moz-range-thumb:hover {
        background: #c9704f;
    }
    
    .slider-labels {
        display: flex;
        justify-content: space-between;
        width: 100%;
        margin-top: 2.5rem;
        font-size: 0.8rem;
        color: #666;
    }
    
    /* Activity details */
    .activity-details-container {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        display: grid;
    }
    
    .activity-level-selection, .duration-selection {
        display: flex;
        flex-direction: column;
    }
    
    .activity-label, .duration-label {
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #444;
    }
    
    .duration-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .duration-value {
        font-weight: 600;
        color: #dd815e;
    }
    
    /* Heat issues details */
    .heat-issues-details {
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .details-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #444;
    }
    
    /* Form actions */
    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .cancel-btn, .submit-btn {
        padding: 0.75rem 4rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .cancel-btn {
        margin: 8px 0px 0px;
        background-color: #f0f0f0;
        color: #444;
        border: none;
    }
    
    .submit-btn {
        background-color: #dd815e;
        color: white;
        border: none;
    }
    
    .cancel-btn:hover {
        background-color: #e0e0e0;
    }
    
    .submit-btn:hover {
        background-color: #c9704f;
    }
    
    .cancel-btn:disabled, .submit-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }
    
    /* Spinner */
    .spinner {
        width: 18px;
        height: 18px;
        border: 3px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Condition cards, medication cards, and heat condition cards */
    .condition-card, .medication-card, .heat-condition-card {
        /* ...existing code... */
        transition: all 0.2s;
    }

    .condition-card.selected, .medication-card.selected, .heat-condition-card.selected {
        background-color: #dd815e; /* Orange main color */
        color: white;
    }

    .condition-card.selected .condition-name, 
    .medication-card.selected .medication-name, 
    .heat-condition-card.selected .condition-name {
        color: white;
    }

    .condition-card.selected .checkbox-indicator, 
    .medication-card.selected .checkbox-indicator, 
    .heat-condition-card.selected .checkbox-indicator {
        opacity: 0; /* Hide the checkbox indicator when selected */
    }

    /* Hide the checkboxes */
    .hidden-checkbox {
        display: none;
    }
</style>
