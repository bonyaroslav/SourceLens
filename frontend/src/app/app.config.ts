import { provideHttpClient } from '@angular/common/http';
import {
  ApplicationConfig,
  provideBrowserGlobalErrorListeners
} from '@angular/core';
import { provideEffects } from '@ngrx/effects';
import { provideState, provideStore } from '@ngrx/store';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { definePreset } from '@primeuix/themes';
import Aura from '@primeuix/themes/aura';
import { providePrimeNG } from 'primeng/config';

import { WorkspaceEffects } from './workspace/state/workspace.effects';
import { workspaceFeature } from './workspace/state/workspace.reducer';

const SourceLensPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '{violet.50}',
      100: '{violet.100}',
      200: '{violet.200}',
      300: '{violet.300}',
      400: '{violet.400}',
      500: '{violet.500}',
      600: '{violet.600}',
      700: '{violet.700}',
      800: '{violet.800}',
      900: '{violet.900}',
      950: '{violet.950}'
    },
    colorScheme: {
      dark: {
        surface: {
          0: '#F4F4F5',
          50: '#F4F4F5',
          100: '#F4F4F5',
          200: '#E4E4E7',
          300: '#D4D4D8',
          400: '#A1A1AA',
          500: '#71717A',
          600: '#52525B',
          700: '#3F3F46',
          800: '#27272A',
          900: '#18181B',
          950: '#09090B'
        },
        primary: {
          color: '#8B5CF6',
          contrastColor: '#F4F4F5',
          hoverColor: '#A78BFA',
          activeColor: '#C4B5FD'
        },
        highlight: {
          background: 'color-mix(in srgb, #8B5CF6, transparent 84%)',
          focusBackground: 'color-mix(in srgb, #8B5CF6, transparent 76%)',
          color: '#F4F4F5',
          focusColor: '#F4F4F5'
        },
        formField: {
          background: '#18181B',
          filledBackground: '#27272A',
          filledHoverBackground: '#27272A',
          filledFocusBackground: '#27272A',
          borderColor: '#3F3F46',
          hoverBorderColor: '#52525B',
          focusBorderColor: '#8B5CF6',
          color: '#F4F4F5',
          disabledColor: '#A1A1AA',
          placeholderColor: '#A1A1AA'
        },
        text: {
          color: '#F4F4F5',
          hoverColor: '#F4F4F5',
          mutedColor: '#A1A1AA',
          hoverMutedColor: '#D4D4D8'
        },
        content: {
          background: '#18181B',
          hoverBackground: '#27272A',
          borderColor: '#3F3F46',
          color: '#F4F4F5',
          hoverColor: '#F4F4F5'
        },
        overlay: {
          select: {
            background: '#18181B',
            borderColor: '#3F3F46',
            color: '#F4F4F5'
          },
          popover: {
            background: '#18181B',
            borderColor: '#3F3F46',
            color: '#F4F4F5'
          },
          modal: {
            background: '#18181B',
            borderColor: '#3F3F46',
            color: '#F4F4F5'
          }
        },
        list: {
          option: {
            focusBackground: '#27272A',
            selectedBackground: 'color-mix(in srgb, #8B5CF6, transparent 84%)',
            selectedFocusBackground: 'color-mix(in srgb, #8B5CF6, transparent 76%)',
            color: '#F4F4F5',
            focusColor: '#F4F4F5',
            selectedColor: '#F4F4F5',
            selectedFocusColor: '#F4F4F5'
          },
          optionGroup: {
            background: 'transparent',
            color: '#A1A1AA'
          }
        }
      }
    }
  }
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideHttpClient(),
    provideAnimationsAsync(),
    provideStore(),
    provideState(workspaceFeature),
    provideEffects(WorkspaceEffects),
    providePrimeNG({
      ripple: false,
      inputVariant: 'filled',
      theme: {
        preset: SourceLensPreset,
        options: {
          darkModeSelector: '.source-lens-app'
        }
      }
    })
  ]
};
