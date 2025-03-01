<script>
    import { createEventDispatcher } from 'svelte';
    import { saveMedicalData } from '$lib/firebase';
    
    export let userId;
    export let initialData = null;
    export let isEditing = false;
    
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
            conditions: [
                { id: 'cardiovascular_disease', label: 'Cardiovascular Disease' },
                { id: 'high_blood_pressure', label: 'High Blood Pressure' }
            ]
        },
        { 
            name: 'Metabolic', 
            conditions: [
                { id: 'diabetes', label: 'Diabetes' },
                { id: 'thyroid_disorder', label: 'Thyroid Disorder' }
            ]
        },
        { 
            name: 'Respiratory', 
            conditions: [
                { id: 'respiratory_issues', label: 'Respiratory Issues' },
                { id: 'asthma', label: 'Asthma' }
            ]
        },
        { 
            name: 'Other Conditions', 
            conditions: [
                { id: 'heat_sensitivity', label: 'Heat Sensitivity' },
                { id: 'kidney_disease', label: 'Kidney Disease' },
                { id: 'neurological_disorders', label: 'Neurological Disorders' }
            ]
        }
    ];
    
    const medicationCategories = [
        {
            name: 'Common Medications',
            medications: [
                { id: 'diuretics', label: 'Diuretics' },
                { id: 'blood_pressure_medications', label: 'Blood Pressure Medications' },
                { id: 'antihistamines', label: 'Antihistamines' },
                { id: 'antidepressants', label: 'Antidepressants' },
                { id: 'antipsychotics', label: 'Antipsychotics' }
            ]
        }
    ];
    
    // Drink types for fluid intake
    const drinkTypes = [
        { id: 'water', label: 'Water' },
        { id: 'electrolyte_drinks', label: 'Electrolyte Drinks' },
        { id: 'coconut_water', label: 'Coconut Water' },
        { id: 'fruit_juice', label: 'Fruit Juice' },
        { id: 'iced_tea', label: 'Iced Tea' },
        { id: 'soda', label: 'Soda' },
        { id: 'milk_tea', label: 'Milk Tea' },
        { id: 'coffee', label: 'Coffee' },
        { id: 'herbal_tea', label: 'Herbal Tea' }
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
            const processedFluidIntake = {};
            
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
            
            const { success: saveSuccess, error: saveError } = await saveMedicalData(userId, processedData);
            
            if (saveSuccess) {
                success = true;
                dispatch('completed', { success: true });
            } else {
                error = saveError || "Failed to save medical data. Please try again.";
            }
        } catch (err) {
            console.error("Error saving medical data:", err);
            error = "An unexpected error occurred. Please try again.";
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

<form on:submit|preventDefault={handleSubmit} class="medical-form">
    <h2>{isEditing ? 'Update Medical Information' : 'Complete Your Medical Profile'}</h2>
    
    {#if !isEditing}
        <p class="form-intro">
            To help us provide personalized insights about your hydration needs, please
            fill out the following health information. Your data is kept private and secure.
        </p>
    {/if}
    
    {#if error}
        <div class="error">{error}</div>
    {/if}
    
    {#if success}
        <div class="success">Your medical data has been successfully saved!</div>
    {/if}
    
    <div class="form-section">
        <h3>Demographics</h3>
        
        <div class="form-row">
            <div class="form-group">
                <label for="age">Age <span class="required">*</span></label>
                <input 
                    type="number" 
                    id="age" 
                    bind:value={medicalData.demographics.age} 
                    min="1" 
                    max="120"
                    required
                />
            </div>
            
            <div class="form-group">
                <label for="gender">Gender</label>
                <select id="gender" bind:value={medicalData.demographics.gender}>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="non-binary">Non-binary</option>
                    <option value="prefer-not-to-say">Prefer not to say</option>
                </select>
            </div>
        </div>
    </div>
    
    <div class="form-section">
        <h3>Biometrics</h3>
        
        <div class="form-row">
            <div class="form-group">
                <label for="height">Height (cm) <span class="required">*</span></label>
                <input 
                    type="number" 
                    id="height" 
                    bind:value={medicalData.biometrics.height} 
                    min="50" 
                    max="250"
                    required
                />
            </div>
            
            <div class="form-group">
                <label for="weight">Weight (kg) <span class="required">*</span></label>
                <input 
                    type="number" 
                    id="weight" 
                    bind:value={medicalData.biometrics.weight} 
                    min="1" 
                    max="500"
                    required
                />
            </div>
        </div>
    </div>
    
    <!-- Organized Medical Conditions -->
    <div class="form-section">
        <h3>Medical Conditions</h3>
        <p class="section-helper">Select any conditions that apply to you</p>
        
        <!-- Loop through each category -->
        {#each medicalConditionCategories as category}
            <fieldset class="condition-group">
                <legend>{category.name}</legend>
                <div class="checkbox-grid">
                    {#each category.conditions as condition}
                        <label class="checkbox-container">
                            <input type="checkbox" bind:checked={medicalData.medical_conditions[condition.id]}>
                            <span class="checkmark"></span>
                            {condition.label}
                        </label>
                    {/each}
                </div>
            </fieldset>
        {/each}
        
        <!-- Other conditions -->
        <div class="other-field">
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.medical_conditions.other.has_other}>
                <span class="checkmark"></span>
                Other condition(s)
            </label>
            
            {#if medicalData.medical_conditions.other.has_other}
                <input 
                    type="text" 
                    placeholder="Please describe" 
                    bind:value={medicalData.medical_conditions.other.description} 
                />
            {/if}
        </div>
    </div>
    
    <!-- Organized Medications -->
    <div class="form-section">
        <h3>Medications</h3>
        <p class="section-helper">Select any medications that you are currently taking</p>
        
        <!-- Loop through each category -->
        {#each medicationCategories as category}
            <fieldset class="condition-group">
                <legend>{category.name}</legend>
                <div class="checkbox-grid">
                    {#each category.medications as medication}
                        <label class="checkbox-container">
                            <input type="checkbox" bind:checked={medicalData.medications[medication.id]}>
                            <span class="checkmark"></span>
                            {medication.label}
                        </label>
                    {/each}
                </div>
            </fieldset>
        {/each}
        
        <!-- Other medications -->
        <div class="other-field">
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.medications.other.has_other}>
                <span class="checkmark"></span>
                Other medication(s)
            </label>
            
            {#if medicalData.medications.other.has_other}
                <input 
                    type="text" 
                    placeholder="Please describe" 
                    bind:value={medicalData.medications.other.description} 
                />
            {/if}
        </div>
    </div>
    
    <!-- Fluid Intake with Sliders -->
    <div class="form-section">
        <h3>Average Daily Fluid Intake</h3>
        <p class="section-helper">Adjust the sliders to indicate how many cups you drink of each fluid type</p>
        
        <div class="fluid-sliders">
            {#each drinkTypes as drink}
                {@const fieldName = drink.id + '_cups'}
                <div class="slider-group">
                    <div class="slider-header">
                        <label for={fieldName}>{drink.label}</label>
                        <span class="slider-value">{formatCups(medicalData.fluid_intake[fieldName])}</span>
                    </div>
                    <input 
                        type="range" 
                        id={fieldName} 
                        bind:value={medicalData.fluid_intake[fieldName]} 
                        min="0" 
                        max="10"
                        step="0.5"
                        class="range-slider" 
                    />
                </div>
            {/each}
            
            <!-- Other fluid with slider -->
            <div class="other-field">
                <label class="checkbox-container">
                    <input type="checkbox" bind:checked={medicalData.fluid_intake.other.has_other}>
                    <span class="checkmark"></span>
                    Other beverage
                </label>
                
                {#if medicalData.fluid_intake.other.has_other}
                    <div class="other-fluid">
                        <input 
                            type="text" 
                            placeholder="Name of beverage" 
                            bind:value={medicalData.fluid_intake.other.name} 
                        />
                        <div class="slider-group">
                            <div class="slider-header">
                                <label for="other_cups">Amount</label>
                                <span class="slider-value">{formatCups(medicalData.fluid_intake.other.cups)}</span>
                            </div>
                            <input 
                                type="range" 
                                id="other_cups" 
                                bind:value={medicalData.fluid_intake.other.cups} 
                                min="0" 
                                max="10"
                                step="0.5"
                                class="range-slider" 
                            />
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    </div>
    
    <div class="form-section">
        <h3>Heat-Related Conditions</h3>
        <p class="section-helper">Select any conditions you have experienced</p>
        
        <div class="checkbox-grid">
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.heat_conditions.mild_dehydration}>
                <span class="checkmark"></span>
                Mild Dehydration
            </label>
            
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_rash}>
                <span class="checkmark"></span>
                Heat Rash
            </label>
            
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_stroke}>
                <span class="checkmark"></span>
                Heat Stroke
            </label>
            
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.heat_conditions.muscle_fatigue}>
                <span class="checkmark"></span>
                Muscle Fatigue
            </label>
            
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_syncope}>
                <span class="checkmark"></span>
                Heat Syncope (Fainting)
            </label>
            
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_edema}>
                <span class="checkmark"></span>
                Heat Edema (Swelling)
            </label>
            
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.heat_conditions.heat_exhaustion}>
                <span class="checkmark"></span>
                Heat Exhaustion
            </label>
        </div>
    </div>
    
    <div class="form-section">
        <h3>Activity & Heat Issues</h3>
        
        <div class="form-group">
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.activity.previous_heat_issues}>
                <span class="checkmark"></span>
                Have you experienced heat-related health issues in the past?
            </label>
        </div>
        
        {#if medicalData.activity.previous_heat_issues}
            <div class="form-group">
                <label for="heat_issues_details">Please describe your experience</label>
                <textarea 
                    id="heat_issues_details" 
                    bind:value={medicalData.activity.heat_issues_details}
                    rows="3"
                ></textarea>
            </div>
        {/if}
        
        <div class="form-group">
            <label class="checkbox-container">
                <input type="checkbox" bind:checked={medicalData.activity.outdoor_activity}>
                <span class="checkmark"></span>
                Do you regularly engage in outdoor activities?
            </label>
        </div>
        
        {#if medicalData.activity.outdoor_activity}
            <div class="form-row">
                <div class="form-group">
                    <label for="activity_level">Activity Level</label>
                    <select id="activity_level" bind:value={medicalData.activity.activity_level}>
                        {#each activityLevels as level}
                            <option value={level.id}>{level.label}</option>
                        {/each}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="activity_duration">Average Duration Per Session</label>
                    <div class="slider-group">
                        <div class="slider-header">
                            <span class="slider-value">{formatDuration(medicalData.activity.activity_duration.value)}</span>
                        </div>
                        <input 
                            type="range" 
                            id="activity_duration" 
                            bind:value={medicalData.activity.activity_duration.value} 
                            min="5" 
                            max="180"
                            step="5"
                            class="range-slider" 
                        />
                        <div class="slider-labels">
                            <span>5 min</span>
                            <span>3 hours</span>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
    </div>
    
    <div class="form-actions">
        {#if isEditing}
            <button type="button" class="cancel-btn" on:click={handleCancel} disabled={loading}>
                Cancel
            </button>
        {/if}
        
        <button type="submit" class="submit-btn" disabled={loading}>
            {#if loading}
                <span class="spinner"></span>
                {isEditing ? 'Updating...' : 'Saving...'}
            {:else}
                {isEditing ? 'Update Profile' : 'Save Profile'}
            {/if}
        </button>
    </div>
</form>

<style>
    /* Add specific styles for the improved form elements */
    
    .condition-group {
        margin-bottom: var(--spacing-md);
        padding: var(--spacing-sm);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
    }
    
    .condition-group legend {
        padding: 0 var(--spacing-xs);
        font-weight: 600;
        color: var(--primary-color);
    }
    
    .checkbox-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: var(--spacing-xs);
    }
    
    .other-field {
        margin-top: var(--spacing-md);
    }
    
    .other-field input[type="text"] {
        margin-top: var(--spacing-xs);
        width: 100%;
    }
    
    .other-fluid {
        margin-top: var(--spacing-xs);
        padding-left: var(--spacing-xl);
    }
    
    .fluid-sliders {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .slider-group {
        width: 100%;
    }
    
    .slider-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: var(--spacing-xs);
    }
    
    .slider-value {
        font-weight: 600;
        color: var(--primary-color);
        min-width: 60px;
        text-align: right;
    }
    
    .range-slider {
        width: 100%;
        cursor: pointer;
        -webkit-appearance: none;
        height: 8px;
        border-radius: 4px;
        background: #ddd;
    }
    
    .range-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--primary-color);
        cursor: pointer;
    }
    
    .range-slider::-moz-range-thumb {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: var(--primary-color);
        cursor: pointer;
        border: none;
    }
    
    .slider-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        color: var(--text-lighter);
        margin-top: 4px;
    }
    
    /* Responsive styles */
    @media (min-width: 576px) {
        .checkbox-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (min-width: 768px) {
        .checkbox-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }
</style>
