import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlateDetectionComponent } from './plate-detection.component';

describe('PlateDetectionComponent', () => {
  let component: PlateDetectionComponent;
  let fixture: ComponentFixture<PlateDetectionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PlateDetectionComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PlateDetectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
