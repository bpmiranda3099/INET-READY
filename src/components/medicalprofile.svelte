<script>
    import { onMount } from 'svelte';
    import { getMedicalData } from '$lib/firebase';
    import MedicalForm from './medicalform.svelte';
    
    export let userId;
    
    let loading = true;
    let error = null;
    let medicalData = null;
    let isEditing = false;
    
    // Constants for unit conversion
    const ML_PER_CUP = 237; // 1 cup = 237 ml (approximately)
    
    // Categories for displaying grouped medical conditions
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
    
    // Drink types for fluid intake
    const drinkTypes = [
        { id: 'water_amount', label: 'Water' },
        { id: 'electrolyte_drinks_amount', label: 'Electrolyte Drinks' },
        { id: 'coconut_water_amount', label: 'Coconut Water' },
        { id: 'fruit_juice_amount', label: 'Fruit Juice' },
        { id: 'iced_tea_amount', label: 'Iced Tea' },
        { id: 'soda_amount', label: 'Soda' },
        { id: 'milk_tea_amount', label: 'Milk Tea' },
        { id: 'coffee_amount', label: 'Coffee' },
        { id: 'herbal_tea_amount', label: 'Herbal Tea' }
    ];
    
    onMount(async () => {
        await loadMedicalData();
    });
    
    async function loadMedicalData() {
        loading = true;
        
        try {
            const { data, error: fetchError } = await getMedicalData(userId);
            
            if (data) {
                medicalData = data;
            } else {
                error = fetchError;
            }
        } catch (err) {
            console.error("Error loading medical data:", err);
            error = "Unable to load medical data. Please try again.";
        } finally {
            loading = false;
        }
    }
    
    function toggleEdit() {
        isEditing = !isEditing;
    }
    
    function handleFormCompleted() {
        isEditing = false;
        loadMedicalData();
    }
    
    function handleFormCancel() {
        isEditing = false;
    }
    
    // Helper functions for formatting display values
    
    // Format activity level for display
    function formatActivityLevel(level) {
        switch(level) {
            case 'sedentary': return 'Sedentary';
            case 'light': return 'Light Activity';
            case 'moderate': return 'Moderate Activity';
            case 'vigorous': return 'Vigorous Activity';
            case 'extreme': return 'Extreme Activity';
            default: return 'Not specified';
        }
    }
    
    // Format activity duration for display
    function formatActivityDuration(duration) {
        switch(duration) {
            case 'less_than_30_mins': return 'Less than 30 minutes';
            case '30_to_60_mins': return '30-60 minutes';
            case '1_to_2_hours': return '1-2 hours';
            case 'more_than_2_hours': return 'More than 2 hours';
            default: return 'Not specified';
        }
    }
    
    // Format gender for display
    function formatGender(gender) {
        switch(gender) {
            case 'male': return 'Male';
            case 'female': return 'Female';
            case 'non-binary': return 'Non-binary';
            case 'prefer-not-to-say': return 'Prefer not to say';
            default: return 'Not specified';
        }
    }
    
    // Get the total daily fluid intake in ml
    function getTotalFluidIntake() {
        if (!medicalData?.fluid_intake) return 0;
        
        let total = 0;
        for (const drinkType of drinkTypes) {
            const amount = medicalData.fluid_intake[drinkType.id] || 0;
            total += amount;
        }
        
        // Add other fluid if any
        if (medicalData.fluid_intake.other_fluid_amount) {
            total += medicalData.fluid_intake.other_fluid_amount;
        }
        
        return total;
    }
    
    // Convert ml to cups for display
    function mlToCups(ml) {
        return Math.round((ml / ML_PER_CUP) * 10) / 10;
    }
    
    // Format fluid amount with both ml and cups
    function formatFluidAmount(ml) {
        if (!ml || ml === 0) return '0 ml (0 cups)';
        const cups = mlToCups(ml);
        return `${ml} ml (${cups} ${cups === 1 ? 'cup' : 'cups'})`;
    }
    
    // Calculate if user drinks enough water per day (simple estimate)
    function getHydrationStatus() {
        if (!medicalData?.biometrics?.weight || !medicalData?.fluid_intake) return null;
        
        // Simple estimate: Person should drink ~30ml per kg of body weight
        const recommendedTotal = medicalData.biometrics.weight * 30;
        const waterAmount = medicalData.fluid_intake.water_amount || 0;
        const totalFluid = getTotalFluidIntake();
        
        if (waterAmount < recommendedTotal * 0.5) {
            return {
                status: 'concern',
                message: 'You may not be drinking enough water. Consider increasing your daily water intake.'
            };
        } else if (totalFluid < recommendedTotal) {
            return {
                status: 'warning',
                message: 'Your total fluid intake is below the recommended amount. Try to drink more fluids throughout the day.'
            };
        } else {
            return {
                status: 'good',
                message: 'Your hydration level appears adequate based on your weight.'
            };
        }
    }
    
    // Get a list of active medical conditions
    function getActiveMedicalConditions() {
        if (!medicalData?.medical_conditions) return [];
        
        const activeConditions = [];
        
        // Collect from all categories
        for (const category of medicalConditionCategories) {
            for (const condition of category.conditions) {
                if (medicalData.medical_conditions[condition.id]) {
                    activeConditions.push(condition.label);
                }
            }
        }
        
        // Add other conditions if specified
        if (medicalData.medical_conditions.other && 
            medicalData.medical_conditions.other.has_other && 
            medicalData.medical_conditions.other.description) {
            activeConditions.push(medicalData.medical_conditions.other.description);
        }
        
        return activeConditions;
    }
    
    // Get a list of active medications
    function getActiveMedications() {
        if (!medicalData?.medications) return [];
        
        const activeMeds = [];
        
        if (medicalData.medications.diuretics) activeMeds.push('Diuretics');
        if (medicalData.medications.blood_pressure_medications) activeMeds.push('Blood Pressure Medications');
        if (medicalData.medications.antihistamines) activeMeds.push('Antihistamines');
        if (medicalData.medications.antidepressants) activeMeds.push('Antidepressants');
        if (medicalData.medications.antipsychotics) activeMeds.push('Antipsychotics');
        
        // Add other medications if specified
        if (medicalData.medications.other && 
            medicalData.medications.other.has_other && 
            medicalData.medications.other.description) {
            activeMeds.push(medicalData.medications.other.description);
        }
        
        return activeMeds;
    }
    
    // Get an array of active heat conditions
    function getActiveHeatConditions() {
        if (!medicalData?.heat_conditions) return [];
        
        const conditions = [];
        
        if (medicalData.heat_conditions.mild_dehydration) conditions.push('Mild Dehydration');
        if (medicalData.heat_conditions.heat_rash) conditions.push('Heat Rash');
        if (medicalData.heat_conditions.heat_stroke) conditions.push('Heat Stroke');
        if (medicalData.heat_conditions.muscle_fatigue) conditions.push('Muscle Fatigue');
        if (medicalData.heat_conditions.heat_syncope) conditions.push('Heat Syncope (Fainting)');
        if (medicalData.heat_conditions.heat_edema) conditions.push('Heat Edema (Swelling)');
        if (medicalData.heat_conditions.heat_exhaustion) conditions.push('Heat Exhaustion');
        
        return conditions;
    }
    
    // Calculate hydration status based on profile data
    $: hydrationStatus = medicalData ? getHydrationStatus() : null;
    $: totalFluidIntake = medicalData ? getTotalFluidIntake() : 0;
    $: medicalConditions = medicalData ? getActiveMedicalConditions() : [];
    $: medications = medicalData ? getActiveMedications() : [];
    $: heatConditions = medicalData ? getActiveHeatConditions() : [];
</script>

<div class="medical-profile">
    {#if loading}
        <div class="loading">
            <span class="spinner"></span>
            <p>Loading medical profile...</p>
        </div>
    {:else if error}
        <div class="error">
            <p>{error}</p>
            <button on:click={loadMedicalData} class="retry-btn">Try Again</button>
        </div>
    {:else if isEditing}
        <MedicalForm 
            {userId} 
            initialData={medicalData} 
            isEditing={true}
            on:completed={handleFormCompleted}
            on:cancel={handleFormCancel}
        />
    {:else if medicalData}
        <div class="profile-header">
            <h3>Medical Profile</h3>
            <button on:click={toggleEdit} class="edit-btn">
                Edit Profile
            </button>
        </div>
        
        <!-- Hydration insight banner -->
        {#if hydrationStatus}
            <div class="insight-banner" class:concern={hydrationStatus.status === 'concern'} class:warning={hydrationStatus.status === 'warning'} class:good={hydrationStatus.status === 'good'}>
                <div class="insight-icon">💧</div>
                <div class="insight-content">
                    <h4>Hydration Insight</h4>
                    <p>{hydrationStatus.message}</p>
                </div>
            </div>
        {/if}
        
        <div class="medical-data">
            <div class="data-section">
                <h4>Demographics & Biometrics</h4>
                <div class="data-grid">
                    <div class="data-item">
                        <span class="data-label">Age:</span>
                        <span class="data-value">{medicalData.demographics?.age || 'Not specified'}</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Gender:</span>
                        <span class="data-value">{formatGender(medicalData.demographics?.gender)}</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Height:</span>
                        <span class="data-value">{medicalData.biometrics?.height || 'Not specified'} cm</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">Weight:</span>
                        <span class="data-value">{medicalData.biometrics?.weight || 'Not specified'} kg</span>
                    </div>
                </div>
            </div>

            <!-- Medical Conditions Section -->
            <div class="data-section">
                <h4>Medical Conditions</h4>
                <div class="condition-list">
                    {#if medicalConditions.length === 0}
                        <p>No medical conditions reported</p>
                    {:else}
                        <ul>
                            {#each medicalConditions as condition}
                                <li>{condition}</li>
                            {/each}
                        </ul>
                    {/if}
                </div>
            </div>

            <!-- Medications Section -->
            <div class="data-section">
                <h4>Medications</h4>
                <div class="condition-list">
                    {#if medications.length === 0}
                        <p>No medications reported</p>
                    {:else}
                        <ul>
                            {#each medications as medication}
                                <li>{medication}</li>
                            {/each}
                        </ul>
                    {/if}
                </div>
            </div>

            <!-- Fluid Intake Section with Visual Representation -->
            <div class="data-section">
                <h4>Daily Fluid Intake</h4>
                
                <div class="fluid-intake-summary">
                    <div class="total-intake">
                        <span class="total-label">Total Daily Intake:</span>
                        <span class="total-value">{formatFluidAmount(totalFluidIntake)}</span>
                    </div>
                    
                    <!-- Visual representation of fluid intake -->
                    <div class="fluid-chart">
                        {#each drinkTypes as drink}
                            {@const amount = medicalData.fluid_intake[drink.id] || 0}
                            {#if amount > 0}
                                <div class="fluid-bar-container">
                                    <div class="fluid-label">{drink.label}</div>
                                    <div class="fluid-bar-wrapper">
                                        <div 
                                            class="fluid-bar" 
                                            style="width: {Math.min(100, (amount / totalFluidIntake) * 100)}%"
                                        ></div>
                                        <span class="fluid-amount">{formatFluidAmount(amount)}</span>
                                    </div>
                                </div>
                            {/if}
                        {/each}
                        
                        {#if medicalData.fluid_intake?.other_fluid && medicalData.fluid_intake?.other_fluid_amount > 0}
                            <div class="fluid-bar-container">
                                <div class="fluid-label">{medicalData.fluid_intake.other_fluid}</div>
                                <div class="fluid-bar-wrapper">
                                    <div 
                                        class="fluid-bar other-fluid-bar" 
                                        style="width: {Math.min(100, (medicalData.fluid_intake.other_fluid_amount / totalFluidIntake) * 100)}%"
                                    ></div>
                                    <span class="fluid-amount">{formatFluidAmount(medicalData.fluid_intake.other_fluid_amount)}</span>
                                </div>
                            </div>
                        {/if}
                    </div>
                    
                    {#if totalFluidIntake === 0}
                        <p>No fluid intake reported</p>
                    {/if}
                </div>
            </div>

            <!-- Heat Conditions Section -->
            <div class="data-section">
                <h4>Heat-Related Conditions</h4>
                <div class="condition-list">
                    {#if heatConditions.length === 0}
                        <p>No heat-related conditions reported</p>
                    {:else}
                        <ul>
                            {#each heatConditions as condition}
                                <li>{condition}</li>
                            {/each}
                        </ul>
                    {/if}
                </div>
            </div>

            <!-- Activity Section -->
            <div class="data-section">
                <h4>Activity & Heat Issues</h4>
                <div class="data-grid">
                    <div class="data-item">
                        <span class="data-label">Previous Heat Issues:</span>
                        <span class="data-value">{medicalData.activity?.previous_heat_issues ? 'Yes' : 'No'}</span>
                    </div>
                    {#if medicalData.activity?.previous_heat_issues && medicalData.activity?.heat_issues_details}
                        <div class="data-item full-width">
                            <span class="data-label">Details:</span>
                            <span class="data-value">{medicalData.activity.heat_issues_details}</span>
                        </div>
                    {/if}
                    <div class="data-item">
                        <span class="data-label">Regular Outdoor Activity:</span>
                        <span class="data-value">{medicalData.activity?.outdoor_activity ? 'Yes' : 'No'}</span>
                    </div>
                    {#if medicalData.activity?.outdoor_activity}
                        <div class="data-item">
                            <span class="data-label">Activity Level:</span>
                            <span class="data-value">{formatActivityLevel(medicalData.activity.activity_level)}</span>
                        </div>
                        <div class="data-item">
                            <span class="data-label">Activity Duration:</span>
                            <span class="data-value">{formatActivityDuration(medicalData.activity.activity_duration)}</span>
                        </div>
                    {/if}
                </div>
            </div>
        </div>
    {:else}
        <div class="empty-medical-profile">
            <h3>No Medical Profile Found</h3>
            <p>Please complete your medical profile to help us provide personalized hydration recommendations.</p>
            <button on:click={toggleEdit} class="submit-btn">Create Medical Profile</button>
        </div>
    {/if}
</div>

<style>
    /* Add styles for the fluid intake visualization */
    .fluid-intake-summary {
        margin-top: var(--spacing-md);
    }
    
    .total-intake {
        display: flex;
        justify-content: space-between;
        font-weight: bold;
        margin-bottom: var(--spacing-md);
        padding-bottom: var(--spacing-xs);
        border-bottom: 1px solid var(--border-color);
    }
    
    .fluid-chart {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .fluid-bar-container {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);
    }
    
    .fluid-label {
        font-weight: 500;
    }
    
    .fluid-bar-wrapper {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
    }
    
    .fluid-bar {
        height: 20px;
        background-color: var(--primary-color);
        border-radius: var(--border-radius);
        transition: width 0.3s ease;
    }
    
    .other-fluid-bar {
        background-color: #8e44ad; /* Different color for other fluids */
    }
    
    .fluid-amount {
        font-size: 0.9rem;
        white-space: nowrap;
    }
    
    /* Insight banner styles */
    .insight-banner {
        display: flex;
        padding: var(--spacing-md);
        border-radius: var(--border-radius);
        margin-bottom: var(--spacing-lg);
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    
    .insight-banner.concern {
        background-color: #ffebee;
        border-left-color: #f44336;
    }
    
    .insight-banner.warning {
        background-color: #fff8e1;
        border-left-color: #ffc107;
    }
    
    .insight-banner.good {
        background-color: #e8f5e9;
        border-left-color: #4caf50;
    }
    
    .insight-icon {
        font-size: 2rem;
        margin-right: var(--spacing-md);
        display: flex;
        align-items: center;
    }
    
    .insight-content {
        flex: 1;
    }
    
    .insight-content h4 {
        margin: 0 0 var(--spacing-xs) 0;
    }
    
    .insight-content p {
        margin: 0;
    }
</style>