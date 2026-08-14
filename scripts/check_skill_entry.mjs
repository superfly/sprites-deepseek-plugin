import { Context } from '@deepseek-ai/cordis'
import SkillRegistry from '@deepseek-ai/dsh-skill'

import * as SpritesSkills from '../index.js'

const ctx = new Context()
const registryFiber = await ctx.plugin(SkillRegistry)
const pluginFiber = await ctx.plugin(SpritesSkills)

try {
  const options = { cwd: process.cwd() }
  const skills = await ctx.skills.list(options)
  const sprites = skills.find((skill) => skill.name === 'sprites')

  if (!sprites) {
    throw new Error('the packaged sprites skill was not discovered')
  }
  if (sprites.provider !== 'sprites') {
    throw new Error(`unexpected skill provider: ${sprites.provider}`)
  }
  if (sprites.source !== 'custom') {
    throw new Error(`unexpected skill source: ${sprites.source}`)
  }

  const loaded = await ctx.skills.get('sprites', options)
  if (!loaded?.content.includes('# Sprites')) {
    throw new Error('the packaged sprites skill body was not loaded')
  }

  console.log('Discovered and loaded the packaged sprites skill.')
} finally {
  await pluginFiber.dispose()
  await registryFiber.dispose()
}
