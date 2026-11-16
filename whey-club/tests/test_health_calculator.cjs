const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const file = path.join(__dirname, '../dist/health-calculator.js');
assert.ok(fs.existsSync(file), 'The calculator must have an executable browser script');
const { calculateHealth } = require(file);
const input = { age: 35, weight: 80, height: 180, sex: 'male', activity: 'moderate', goal: 'maintain' };

// Hand-checked: REE 1755 kcal; activity 1.55 gives 2720.25 kcal.
const result = calculateHealth(input);
assert.equal(result.resting, 1755);
assert.equal(result.maintenance, 2720);
assert.equal(result.calories, 2720);
assert.equal(calculateHealth({ ...input, goal: 'lose' }).calories, 2310);
assert.equal(calculateHealth({ ...input, goal: 'gain' }).calories, 2990);
assert.equal(calculateHealth({ ...input, sex: 'female' }).resting, 1589);
assert.equal(calculateHealth({ ...input, activity: 'sedentary' }).maintenance, 2110);
assert.deepEqual(result.protein, [128, 176]);
assert.deepEqual(result.perMeal, [32, 44]);
assert.equal(result.bmi, 24.7);
assert.equal(result.bmiCategory, 'normal');
assert.equal(calculateHealth({ ...input, weight: 85 }).bmiCategory, 'overweight');
assert.equal(calculateHealth({ ...input, weight: 98 }).bmiCategory, 'obesity');
for (const [weight, category] of [[74, 'normal'], [100, 'overweight'], [120, 'obesity']]) {
  assert.equal(calculateHealth({ ...input, height: 200, weight }).bmiCategory, category);
}
assert.equal(calculateHealth({ ...input, weight: 80.99 }).bmiCategory, 'normal', 'Classify BMI before rounding its display');

// Persian and Arabic numerals must work through the same calculation path.
assert.deepEqual(calculateHealth({ ...input, age: '۳۵', weight: '٨٠', height: '۱۸۰' }), result);
assert.equal(calculateHealth({ ...input, weight: '۸۰٫۵' }).protein[0], 129);
for (const [field, value] of [['age', 19], ['age', 81], ['age', 30.5], ['age', ''], ['weight', 0], ['weight', 251], ['weight', Infinity], ['height', 129], ['height', NaN], ['weight', '80kg'], ['sex', 'other'], ['activity', '9'], ['activity', '__proto__'], ['goal', 'rapid-loss'], ['goal', 'constructor']]) {
  assert.throws(() => calculateHealth({ ...input, [field]: value }), error => error.field === field);
}

const underweight = calculateHealth({ ...input, weight: 50, goal: 'lose' });
assert.equal(underweight.bmiCategory, 'underweight');
assert.equal(underweight.calories, null, 'Do not suggest weight loss at a low BMI');
assert.ok(underweight.calorieNote);
const highBmi = calculateHealth({ ...input, weight: 120 });
assert.equal(highBmi.protein, null, 'Do not overestimate protein using total body weight at high BMI');
assert.equal(highBmi.perMeal, null);
assert.ok(highBmi.proteinNote);
const lowEstimate = calculateHealth({ age: 80, weight: 35, height: 130, sex: 'female', activity: 'sedentary', goal: 'lose' });
assert.equal(lowEstimate.calories, null, 'Unusually low estimates need individual review');
assert.ok(lowEstimate.calorieNote);
console.log('Passed: calorie goals, sex/activity factors, protein, meals, BMI, Persian/Arabic numbers, validation and unsuitable targets.');
