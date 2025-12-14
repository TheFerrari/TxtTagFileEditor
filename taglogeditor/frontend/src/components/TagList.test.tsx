import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import React from 'react'
import { TagList } from './TagList'

const counts = {
  general: { water: 6, fire: 3 },
  artist: { alice: 2 },
}

describe('TagList', () => {
  it('renders namespaces with matching tags', () => {
    const { getByText } = render(
      <TagList counts={counts} search="water" minCount={1} onToggle={() => {}} selected={{}} />,
    )
    expect(getByText('general')).toBeTruthy()
    expect(getByText('water')).toBeTruthy()
  })
})
