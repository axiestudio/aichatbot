import { describe, it, expect } from 'vitest'

describe('Basic Tests', () => {
  it('should perform basic math operations', () => {
    expect(1 + 1).toBe(2)
    expect(2 * 3).toBe(6)
    expect(10 / 2).toBe(5)
  })

  it('should handle string operations', () => {
    expect('hello' + ' world').toBe('hello world')
    expect('test'.toUpperCase()).toBe('TEST')
    expect('hello'.length).toBe(5)
  })

  it('should handle array operations', () => {
    const testArray = [1, 2, 3]
    expect(testArray.length).toBe(3)
    expect(testArray[0]).toBe(1)
    testArray.push(4)
    expect(testArray.length).toBe(4)
  })

  it('should handle object operations', () => {
    const testObj = { key: 'value' }
    expect(testObj.key).toBe('value')
    testObj.newKey = 'new value'
    expect(Object.keys(testObj).length).toBe(2)
  })
})